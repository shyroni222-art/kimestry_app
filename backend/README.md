# Kimestry-Benchmark - Schema and Column Matching System

## Project Overview

Kimestry-Benchmark is an LLM-powered schema and column matching system designed to automatically align user-provided tables (usually Excel files) with the correct database schemas and column names. The system addresses the common problem where users upload local tables whose structure and column names differ from official database schemas.

## Key Features

- **Schema Matching**: Automatically identifies the correct schema in the corresponding environment for uploaded tables
- **Column Mapping**: Maps table columns to the correct database format
- **Multi-Environment Support**: Tables belong to specific environments and can only be matched within their respective environment
- **Flexible Pipeline Architecture**: Support for custom pipeline names and routes
- **Benchmarking**: Comprehensive benchmarking system to evaluate and compare different pipelines
- **Data Persistence**: Results stored in PostgreSQL database with detailed metrics
- **API Interface**: FastAPI-based REST API for easy integration

## System Architecture

- **Frontend**: FastAPI web application with automatic API documentation
- **Processing**: Pipeline system with n8n integration for workflow execution
- **Data Storage**: PostgreSQL database for persistent storage of results and metrics
- **External APIs**: Integration with external schema APIs
- **File Processing**: Excel file handling with pandas for data manipulation

## Prerequisites

- Python 3.8+
- Docker Desktop (for PostgreSQL container)
- pip (Python package manager)

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables**
   Create a `.env` file in the backend directory to configure the application:
   ```bash
   cp .env.example .env
   ```
   
   The application uses the following environment variables:
   - `POSTGRES_CONNECTION_STRING` - PostgreSQL connection string (default: `postgresql://user:password@localhost:5433/kimestry`)
   - `MICK_API_BASE_URL` - Base URL for external schema API (default: `http://localhost:8080/api`)
   - `EXCEL_FILES_DIR` - Directory for Excel files (default: `./data/excels`)
   - `GROUND_TRUTH_DIR` - Directory for ground truth data (default: `./data/ground_truth`)
   - `RESULTS_DIR` - Directory for results (default: `./data/results`)
   - `N8N_URL` - URL for n8n webhook (default: `https://ronihabaishan.app.n8n.cloud/webhook/schema-matching`)
   - `PORT` - Server port (default: `8000`)

## Running the Application

### Using the Easy Testing Script
The project includes a comprehensive script for easy testing:

```bash
# Run both PostgreSQL and the Kimestry server
python run_kimestry.py run

# View saved pipeline data in PostgreSQL
python run_kimestry.py view_data

# View saved benchmark data in PostgreSQL
python run_kimestry.py view_benchmarks

# Clean up test files
python run_kimestry.py cleanup

# Clear all data from PostgreSQL tables
python run_kimestry.py clear_pg

# Run benchmark for all Excel files in environment directories
python run_kimestry.py run_benchmarks

# Run full benchmark
python run_kimestry.py run_full_benchmark
```

### Manual Startup
1. **Start PostgreSQL Container**
   ```bash
   docker run --name kimestry-postgres -e POSTGRES_DB=kimestry -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5433:5432 -d postgres:13
   ```

2. **Start the FastAPI Server**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## API Endpoints

For detailed information about all API endpoints, see [backend.md](backend.md).

Key endpoints for the frontend:
- `GET /api/v1/benchmark` - Get benchmark results for all pipelines (returns column+schema accuracy, schema accuracy, total tests, and wrong matches)
- `GET /api/v1/benchmark/{pipeline_name}` - Get benchmark results for a specific pipeline (includes detailed wrong matches)

## Frontend Integration

### Leaderboard Feature
The system supports a leaderboard feature for displaying benchmark results. The leaderboard can be updated by calling the `/api/v1/benchmark` endpoint, which returns benchmark results for all pipelines in the database.

## Development

### Code Structure
```
src/
├── main.py                 # FastAPI application entry point
├── routes/                 # API route definitions
├── pipeline/               # Pipeline processing logic
│   └── pipelines/          # Individual pipeline implementations
├── providers/              # External service integrations
├── benchmarking/           # Benchmarking functionality
├── utils/                  # Utility functions and constants
└── data/                   # Data storage directories
```

### Pipeline Development
- The n8n pipeline always runs, but custom names and routes can be specified
- Pipeline names used in the system are the names saved in the database
- Pipeline routes specify which n8n webhook to use

### Testing and Benchmarking
- The system includes comprehensive benchmarking capabilities
- Results are automatically saved to PostgreSQL for analysis
- Mock testing available for development without external dependencies

### Error Handling
- All server errors properly return 500 status codes with error explanations
- Validation errors return 400 status codes
- Missing resources return 404 status codes

## Frontend Development

For frontend developers looking to create a dashboard or interface for Kimestry:

1. The main leaderboard can be populated by calling `GET /api/v1/benchmark` which returns results for all pipelines
2. Individual pipeline results can be fetched using `GET /api/v1/benchmark/{pipeline_name}`
3. The leaderboard can be updated by calling a `POST /benchmark` to run new benchmarks
4. Use `POST /pipeline/run` to run individual pipelines with custom names and routes

## Configuration
- All configuration is centralized in `src/utils/constants.py`
- Environment variables can override default configuration values
- The system is designed to work with n8n workflows for processing

## Key Components

### Pipeline System
- `N8NPipeline`: The main pipeline that sends Excel files to n8n workflows for processing
- Pipelines can be run with custom names and routes
- Pipeline results are stored in PostgreSQL with the custom name provided

### Data Providers
- `n8n.py`: Provider for n8n workflow integration
- `postgress.py`: PostgreSQL database integration
- `mick.py`: Integration with external schema API

### Benchmark System
- Comprehensive benchmarking with column+schema accuracy and schema accuracy metrics (removed other metrics)
- Stores results in PostgreSQL for comparison and analysis
- Supports execution across multiple environments
- Returns detailed wrong matches information for analysis

### File and Data Management
- Excel file processing using pandas and openpyxl
- Automatic directory creation for data storage
- Temporary file handling with proper cleanup

## Best Practices

1. Always provide meaningful names for your pipelines when running them
2. Use appropriate n8n routes for different types of processing
3. Regularly run benchmarking to track performance
4. Use the mock provider for testing without external dependencies
5. Monitor the logs for any processing errors or issues