from fastapi import FastAPI, HTTPException, UploadFile, File, BackgroundTasks, Body
from pydantic import BaseModel
from typing import Dict, Any
import os
import uuid
import pandas as pd
from app.core.config import CSV_DIR

from app.data import fetching, processing, manipulation
from app.scheduler import jobs

app = FastAPI(
    title="808Found Backend",
    description="API for fetching stock data, running backtests, and managing data manipulation tasks.",
    version="1.0.0",
)

# In-memory store for backtest tasks
backtest_tasks: Dict[str, Dict[str, Any]] = {}

class ManipulationConfig(BaseModel):
    filter_column: str
    filter_value: Any

@app.on_event("startup")
def startup_event():
    """
    Start the scheduler on application startup.
    """
    jobs.start_scheduler()

@app.get("/")
def read_root():
    """
    Root endpoint to check if the API is running.
    """
    return {"message": "Welcome to the 808Found Backend API!"}

@app.post("/data/fetch", summary="Fetch real-time stock data")
def fetch_data():
    """
    Triggers the data fetching process to update the stock data.
    """
    try:
        result = fetching.update_all_data()
        return {"message": "Data fetching completed successfully.", "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/backtest", summary="Run a backtest")
def run_backtest(config: Dict[str, Any] = Body(None)):
    """
    Runs the backtesting process with the given configuration.
    If no configuration is provided, it uses the default configuration.
    """
    try:
        if config is None or not config: # Check if config is None or empty
            config = processing.CONFIG
        trades_df, metrics, equity_curve_data = processing.run_backtest(config)
        return {
            "message": "Backtest completed successfully.",
            "metrics": metrics,
            "trades": trades_df.to_dict("records"),
            "equity_curve": equity_curve_data,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

async def _run_backtest_task(task_id: str, config: Dict[str, Any]):
    """
    Helper function to run the backtest in the background and update task status.
    """
    try:
        backtest_tasks[task_id]["status"] = "RUNNING"
        trades_df, metrics, equity_curve_data = processing.run_backtest(config)
        backtest_tasks[task_id]["status"] = "COMPLETED"
        backtest_tasks[task_id]["result"] = {
            "metrics": metrics,
            "trades": trades_df.to_dict("records"),
            "equity_curve": equity_curve_data,
        }
    except Exception as e:
        backtest_tasks[task_id]["status"] = "FAILED"
        backtest_tasks[task_id]["error"] = str(e)

@app.post("/backtest/start", summary="Start an asynchronous backtest")
async def start_backtest(background_tasks: BackgroundTasks, config: Dict[str, Any] = Body(None)):
    """
    Starts a backtesting process in the background and returns a task ID.
    """
    task_id = str(uuid.uuid4())
    backtest_tasks[task_id] = {"status": "PENDING", "result": None, "error": None}

    if config is None or not config:
        config = processing.CONFIG

    background_tasks.add_task(_run_backtest_task, task_id, config)
    return {"message": "Backtest started in the background.", "task_id": task_id}

@app.get("/backtest/status/{task_id}", summary="Get backtest status")
def get_backtest_status(task_id: str):
    """
    Checks the status and progress of a running backtest.
    """
    task = backtest_tasks.get(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="Task ID not found.")
    return {"task_id": task_id, "status": task["status"], "result": task["result"], "error": task["error"]}

@app.post("/data/manipulate", summary="Manipulate data")
def manipulate_data_endpoint(config: ManipulationConfig):
    """
    Performs data manipulation based on the provided configuration.
    """
    try:
        # This is a placeholder. In a real application, you would load a DataFrame
        # from a source (e.g., a CSV file or a database) and then manipulate it.
        df = processing.load_data(processing.CONFIG)
        manipulated_df = manipulation.manipulate_data(df, config.dict())
        return {
            "message": "Data manipulation completed successfully.",
            "manipulated_data": manipulated_df.to_dict("records"),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

from app.core.config import CSV_DIR # Already imported, just ensuring it's there

# ...

@app.post("/data/upload", summary="Upload a CSV file")
async def upload_csv_file(file: UploadFile = File(...)):
    """
    Uploads a CSV file to the backend/csv directory.
    """
    try:
        file_path = os.path.join(CSV_DIR, file.filename)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())
        return {"message": f"File '{file.filename}' uploaded successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Could not upload file: {e}")

@app.get("/stocks", summary="Get available stocks")
def get_available_stocks():
    """
    Returns a list of available stocks from the nifty500.csv file.
    """
    try:
        nifty_file_path = os.path.join(CSV_DIR, "nifty500.csv")
        if not os.path.exists(nifty_file_path):
            raise HTTPException(status_code=404, detail="nifty500.csv not found.")
        
        df = pd.read_csv(nifty_file_path)
        # Assuming the CSV has a column named 'Symbol' or 'Company Name'
        # Adjust column name as per actual CSV structure
        if 'Symbol' in df.columns:
            return {"stocks": df['Symbol'].tolist()}
        elif 'Company Name' in df.columns:
            return {"stocks": df['Company Name'].tolist()}
        else:
            return {"stocks": df.iloc[:, 0].tolist()} # Fallback to first column
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
