# 808Found Backend API for Gemini Instances

This document provides a detailed overview of the 808Found Backend API endpoints and configuration, specifically tailored for consumption by an AI agent or another Gemini instance.

## Base URL

The base URL for all API endpoints is typically `http://localhost:8000` during local development, or a deployed URL in production.

## API Endpoints

### 1. Root Endpoint

*   **Path**: `/`
*   **Method**: `GET`
*   **Summary**: Checks if the API is running.
*   **Description**: A simple health check endpoint.
*   **Response**:
    ```json
    {
        "message": "Welcome to the 808Found Backend API!"
    }
    ```

### 2. Fetch Real-time Stock Data

*   **Path**: `/data/fetch`
*   **Method**: `POST`
*   **Summary**: Triggers the data fetching process to update stock data.
*   **Description**: Initiates an internal process to fetch and update stock market data. This operation can be time-consuming.
*   **Request Body**: None
*   **Response (Success)**:
    ```json
    {
        "message": "Data fetching completed successfully.",
        "result": "Details about the fetching process, e.g., number of stocks updated."
    }
    ```
*   **Response (Error)**:
    ```json
    {
        "detail": "Error message"
    }
    ```
    *   **Status Code**: `500 Internal Server Error`

### 3. Run a Synchronous Backtest

*   **Path**: `/data/backtest`
*   **Method**: `POST`
*   **Summary**: Runs a backtesting process with a given configuration.
*   **Description**: Executes a backtest synchronously. The response will contain the backtest results once completed. If no configuration is provided, it uses a default configuration.
*   **Request Body (Optional)**:
    ```json
    {
        "strategy_name": "MovingAverageCrossover",
        "start_date": "2020-01-01",
        "end_date": "2021-12-31",
        "initial_capital": 100000,
        "parameters": {
            "short_window": 20,
            "long_window": 50
        }
    }
    ```
    *   The exact structure of the `config` dictionary depends on the backtesting logic implemented in `app/data/processing.py`.
*   **Response (Success)**:
    ```json
    {
        "message": "Backtest completed successfully.",
        "metrics": {
            "total_return": 0.15,
            "sharpe_ratio": 1.2,
            "max_drawdown": -0.10
        },
        "trades": [
            {
                "date": "2020-03-10",
                "symbol": "AAPL",
                "type": "BUY",
                "price": 100.50,
                "quantity": 10
            }
        ],
        "equity_curve": [
            {"date": "2020-01-01", "value": 100000},
            {"date": "2020-01-02", "value": 100150}
        ]
    }
    ```
*   **Response (Error)**:
    ```json
    {
        "detail": "Error message"
    }
    ```
    *   **Status Code**: `500 Internal Server Error`

### 4. Start an Asynchronous Backtest

*   **Path**: `/backtest/start`
*   **Method**: `POST`
*   **Summary**: Starts a backtesting process in the background and returns a task ID.
*   **Description**: Useful for long-running backtests. The client can poll the `/backtest/status/{task_id}` endpoint to check the progress and retrieve results.
*   **Request Body (Optional)**: Same as `/data/backtest`.
*   **Response (Success)**:
    ```json
    {
        "message": "Backtest started in the background.",
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    }
    ```

### 5. Get Backtest Status

*   **Path**: `/backtest/status/{task_id}`
*   **Method**: `GET`
*   **Summary**: Checks the status and progress of a running backtest.
*   **Description**: Retrieves the current status, and if completed, the results of an asynchronous backtest identified by `task_id`.
*   **Path Parameters**:
    *   `task_id` (string, required): The unique identifier for the backtest task, obtained from `/backtest/start`.
*   **Response (Pending/Running)**:
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "status": "PENDING"
    }
    ```
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "status": "RUNNING"
    }
    ```
*   **Response (Completed)**:
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "status": "COMPLETED",
        "result": {
            "metrics": { ... },
            "trades": [ ... ],
            "equity_curve": [ ... ]
        },
        "error": null
    }
    ```
*   **Response (Failed)**:
    ```json
    {
        "task_id": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
        "status": "FAILED",
        "result": null,
        "error": "Detailed error message"
    }
    ```
*   **Response (Error - Task Not Found)**:
    ```json
    {
        "detail": "Task ID not found."
    }
    ```
    *   **Status Code**: `404 Not Found`

### 6. Manipulate Data

*   **Path**: `/data/manipulate`
*   **Method**: `POST`
*   **Summary**: Performs data manipulation based on the provided configuration.
*   **Description**: Applies specified filtering or other manipulation techniques to a dataset. The exact behavior depends on the `manipulation.py` implementation.
*   **Request Body**:
    ```json
    {
        "filter_column": "Symbol",
        "filter_value": "AAPL"
    }
    ```
    *   The `ManipulationConfig` Pydantic model expects `filter_column` (string) and `filter_value` (any type).
*   **Response (Success)**:
    ```json
    {
        "message": "Data manipulation completed successfully.",
        "manipulated_data": [
            {"column1": "value1", "column2": "value2"},
            {"column1": "value3", "column2": "value4"}
        ]
    }
    ```
*   **Response (Error)**:
    ```json
    {
        "detail": "Error message"
    }
    ```
    *   **Status Code**: `500 Internal Server Error`

### 7. Upload a CSV File

*   **Path**: `/data/upload`
*   **Method**: `POST`
*   **Summary**: Uploads a CSV file to the backend/csv directory.
*   **Description**: Allows clients to upload CSV files, which can then be used by other parts of the application (e.g., for backtesting data).
*   **Request Body**: `multipart/form-data`
    *   `file`: The CSV file to upload.
*   **Response (Success)**:
    ```json
    {
        "message": "File 'your_file_name.csv' uploaded successfully."
    }
    ```
*   **Response (Error)**:
    ```json
    {
        "detail": "Could not upload file: error message"
    }
    ```
    *   **Status Code**: `500 Internal Server Error`

### 8. Get Available Stocks

*   **Path**: `/stocks`
*   **Method**: `GET`
*   **Summary**: Returns a list of available stocks.
*   **Description**: Retrieves a list of stock symbols or names, typically sourced from `nifty500.csv`.
*   **Request Body**: None
*   **Response (Success)**:
    ```json
    {
        "stocks": ["AAPL", "GOOGL", "MSFT", ...]
    }
    ```
*   **Response (Error - File Not Found)**:
    ```json
    {
        "detail": "nifty500.csv not found."
    }
    ```
    *   **Status Code**: `404 Not Found`
*   **Response (Error)**:
    ```json
    {
        "detail": "Error message"
    }
    ```
    *   **Status Code**: `500 Internal Server Error`

## Configuration Details

The backend's behavior can be influenced by environment variables, which override default values set in `app/core/config.py`. When interacting with or deploying this backend, consider setting these variables as needed.

| Environment Variable    | Default Value     | Description                                                              |
| :---------------------- | :---------------- | :----------------------------------------------------------------------- |
| `TIMEZONE`              | `Asia/Kolkata`    | Timezone used by the scheduler for task scheduling.                      |
| `SCHEDULE_HOUR`         | `16`              | Hour (24-hour format) when scheduled tasks are set to run.               |
| `SCHEDULE_MINUTE`       | `0`               | Minute when scheduled tasks are set to run.                              |
| `YFINANCE_THREADS`      | `6`               | Number of threads used for fetching data via YFinance.                   |
| `HTTP_RETRY_TOTAL`      | `5`               | Total number of retries for HTTP requests in data fetching.              |
| `HTTP_BACKOFF`          | `1.0`             | Backoff factor for retrying HTTP requests.                               |

---
