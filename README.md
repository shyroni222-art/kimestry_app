# Kimestry - Schema and Column Matching System

## Project Overview

This is the main repository for Kimestry - an LLM-powered schema and column matching system designed to automatically align user-provided tables (usually Excel files) with the correct database schemas and column names.

## Project Structure

The project is organized into two main parts:

- `backend/` - Contains the Python FastAPI application and all backend services
- `frontend/` - Contains the React frontend application with pipeline benchmark leaderboard

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

The frontend is built with React and provides:
- A beautiful, responsive leaderboard of pipeline benchmarks
- Real-time updating of benchmark metrics
- Interactive charts and visualizations
- Performance statistics for all pipelines
- Auto-refreshing data from the backend API

### Features
- Real-time leaderboard with pipeline rankings
- Accuracy metrics visualization (column+schema accuracy and schema accuracy)
- Auto-refreshing data (every 30 seconds)
- Responsive design for all screen sizes
- Beautiful animations and transitions
- Performance statistics breakdown
- Pipeline detail pages showing correct vs incorrect results
- Search functionality for pipelines
- Interactive navigation between leaderboard and pipeline details

### Setup
1. Navigate to the `frontend/` directory
2. Install dependencies: `npm install`
3. Start the development server: `npm start`

### Configuration
The frontend connects to the backend API at http://localhost:8000 by default. To change this, update the `API_BASE_URL` constant in `frontend/src/App.js`.

## Setup

### Backend Setup
1. Navigate to the `backend/` directory
2. Install dependencies: `pip install -r requirements.txt`
3. Follow the backend-specific setup instructions in [backend/README.md](backend/README.md)

### Frontend Setup
1. Navigate to the `frontend/` directory
2. Install dependencies: `npm install`
3. Start the development server: `npm start`
4. The frontend will be available at http://localhost:3000

## Running the Application

### Development Mode (Separate Processes)
For development, you can run the backend and frontend separately:

#### Backend
1. Go to the `backend/` directory
2. Use the easy testing script: `python run_kimestry.py run`
3. Or start the server manually: `uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload`
4. Or use the development script: `python run_development.py`

#### Frontend
1. Go to the `frontend/` directory
2. Install dependencies: `npm install`
3. Start the development server: `npm start`
4. The frontend will automatically open in your browser at http://localhost:3000

### Docker Mode (Recommended for Production)
For the full application stack including proxy configuration:

```bash
# From the project root directory
docker-compose up --build
```

The application will be available at http://localhost

### Environment Configuration
The application uses environment variables for configuration. For development, you can:
- Set environment variables directly
- Use the provided `.env` file by copying it to your environment
- The application will use sensible defaults if variables are not set

## Contributing

Contributions to both backend and frontend are welcome. Please follow the respective documentation for each part of the project.

## License

See the LICENSE file in the backend directory for details.