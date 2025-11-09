# 808Found Backend

This repository contains the backend API for the 808Found project, built with FastAPI. It provides functionalities for fetching real-time stock data, running backtests, manipulating data, uploading files, and managing scheduled tasks.

## Features

*   **Stock Data Fetching**: Retrieve real-time stock data.
*   **Backtesting Engine**: Run synchronous and asynchronous backtests with configurable strategies.
*   **Data Manipulation**: Perform various data manipulation operations.
*   **CSV Upload**: Upload CSV files to the server.
*   **Stock Listing**: Get a list of available stocks.
*   **Scheduled Tasks**: Manage and execute scheduled data updates.

## Setup

### Prerequisites

*   Python 3.8+
*   `pip` (Python package installer)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd 808Found/backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To start the FastAPI server, navigate to the `backend` directory and run:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be accessible at `http://0.0.0.0:8000`.

## API Endpoints

A detailed description of all available API endpoints, their request/response formats, and examples can be found in `gemini.md`.

## Configuration

The application uses configuration settings defined in `app/core/config.py`. Some settings can be overridden using environment variables:

*   `TIMEZONE`: Timezone for scheduler (default: `Asia/Kolkata`)
*   `SCHEDULE_HOUR`: Hour for scheduled tasks (default: `16`)
*   `SCHEDULE_MINUTE`: Minute for scheduled tasks (default: `0`)
*   `YFINANCE_THREADS`: Number of threads for YFinance data fetching (default: `6`)
*   `HTTP_RETRY_TOTAL`: Total retries for HTTP requests (default: `5`)
*   `HTTP_BACKOFF`: Backoff factor for HTTP retries (default: `1.0`)

---
