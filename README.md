# Kimestry - Schema and Column Matching System

## Project Overview

This is the main repository for Kimestry - an LLM-powered schema and column matching system designed to automatically align user-provided tables (usually Excel files) with the correct database schemas and column names.

## Project Structure

The project is organized into two main parts:

- `backend/` - Contains the Python FastAPI application and all backend services
- `frontend/` - Reserved for the frontend application (to be implemented)

## Backend

The backend is built with Python and FastAPI and handles:
- Schema matching algorithms
- Column mapping
- Benchmarking system
- API endpoints
- Database connections
- n8n workflow integration

For detailed backend documentation, see [backend/README.md](backend/README.md) and [backend/backend.md](backend/backend.md).

## Frontend

The frontend is planned to provide:
- A dashboard for monitoring pipeline results
- A leaderboard of pipeline benchmarks
- User interface for running pipelines
- Data visualization tools

## Setup

### Backend Setup
1. Navigate to the `backend/` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Follow the backend-specific setup instructions in [backend/README.md](backend/README.md)

### Frontend Setup
Instructions will be added when the frontend is implemented.

## Running the Application

### Backend
1. Go to the `backend/` directory
2. Use the easy testing script: `python run_kimestry.py run`
3. Or start the server manually: `uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload`

## Contributing

Contributions to both backend and frontend are welcome. Please follow the respective documentation for each part of the project.

## License

See the LICENSE file in the backend directory for details.