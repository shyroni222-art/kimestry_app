# Kimestry - Schema and Column Matching System

## Project Overview

Kimestry is an LLM-powered schema and column matching system designed to automatically align user-provided tables (usually Excel files) with the correct database schemas and column names. The system addresses the common problem where users upload local tables whose structure and column names differ from official database schemas.

### Key Features
- **Schema Matching**: Automatically identifies the correct schema in the corresponding environment for uploaded tables
- **Column Mapping**: Maps table columns to the correct database format
- **Multi-Environment Support**: Tables belong to specific environments and can only be matched within their respective environment
- **Pipeline Architecture**: Flexible pipeline system for different matching strategies
- **Benchmarking**: Comprehensive benchmarking system to evaluate and compare different pipelines
- **Data Persistence**: Results stored in PostgreSQL database with detailed metrics
- **API Interface**: FastAPI-based REST API for easy integration

### System Architecture
- **Frontend**: FastAPI web application with automatic API documentation
- **Processing**: Pipeline system with n8n integration for workflow execution
- **Data Storage**: PostgreSQL database for persistent storage of results and metrics
- **External APIs**: Integration with Mick API for database schema retrieval
- **File Processing**: Excel file handling with pandas for data manipulation

## Building and Running

### Prerequisites
- Python 3.8+
- Docker Desktop (for PostgreSQL container)
- pip (Python package manager)

### Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Variables** (Optional)
   The application uses the following environment variables:
   - `POSTGRES_CONNECTION_STRING` - PostgreSQL connection string (default: `postgresql://user:password@localhost:5433/kimestry`)
   - `MICK_API_BASE_URL` - Base URL for Mick API (default: `http://localhost:8080/api`)
   - `EXCEL_FILES_DIR` - Directory for Excel files (default: `./data/excels`)
   - `GROUND_TRUTH_DIR` - Directory for ground truth data (default: `./data/ground_truth`)
   - `RESULTS_DIR` - Directory for results (default: `./data/results`)

### Running the Application

#### Using the Easy Testing Script
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

#### Manual Startup
1. **Start PostgreSQL Container**
   ```bash
   docker run --name kimestry-postgres -e POSTGRES_DB=kimestry -e POSTGRES_USER=user -e POSTGRES_PASSWORD=password -p 5433:5432 -d postgres:13
   ```

2. **Start the FastAPI Server**
   ```bash
   uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
   ```

### API Endpoints

- `GET /` - Health check and basic info
- `GET /docs` - Interactive API documentation (Swagger UI)
- `GET /redoc` - Alternative API documentation (ReDoc)
- `POST /api/v1/pipeline/run` - Run a pipeline on an uploaded Excel file
- `POST /api/v1/benchmark` - Run benchmark for a specific pipeline
- `GET /api/v1/benchmark/{pipeline_name}` - Get benchmark results for a specific pipeline
- `GET /api/v1/benchmark` - Get benchmark results for all pipelines

## Development Conventions

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
- All pipelines should inherit from `AbstractPipeline`
- Implement the `run` method with the specific processing logic
- Current implementation supports only the n8n pipeline (`n8n_pipeline`)

### Testing and Benchmarking
- The system includes comprehensive benchmarking capabilities
- Results are automatically saved to PostgreSQL for analysis
- Mock testing available for development without external dependencies

### Configuration
- All configuration is centralized in `src/utils/constants.py`
- Environment variables can override default configuration values
- The system currently supports only the n8n pipeline as specified in the requirements

## Key Components

### Pipeline System
- `N8NPipeline`: The main pipeline that sends Excel files to n8n workflows for processing
- AbstractPipeline: Base class for all pipeline implementations
- Pipeline results are stored in PostgreSQL with detailed metadata

### Data Providers
- `n8n.py`: Provider for n8n workflow integration
- `postgress.py`: PostgreSQL database integration
- `mick.py`: Integration with external schema API

### Benchmark System
- Comprehensive benchmarking with multiple accuracy metrics
- Stores results in PostgreSQL for comparison and analysis
- Supports execution across multiple environments

### File and Data Management
- Excel file processing using pandas and openpyxl
- Automatic directory creation for data storage
- Temporary file handling with proper cleanup