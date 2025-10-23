# Kimestry-Benchmark Backend API Documentation

## Overview
Kimestry-Benchmark is an LLM-powered schema and column matching system designed to automatically align user-provided tables (usually Excel files) with the correct database schemas and column names.

## API Base URL
All API endpoints are prefixed with `/api/v1/`

## Authentication
No authentication required for any endpoints.

## Endpoints

### Pipeline Routes

#### POST /pipeline/run
Run the n8n pipeline on an uploaded Excel file using the specified route.

**Parameters (form data):**
- `file` (File, required): Excel file to process
- `pipeline_name` (string, required): Name to save in the database for this pipeline run
- `env_id` (string, optional): Environment ID (default: "default_env")
- `pipeline_route` (string, required): The route to use for the n8n pipeline

**Response:**
```json
{
  "job_id": "string",
  "pipeline_name": "string", 
  "env_id": "string",
  "results": [
    {
      "original_column": "string",
      "fitted_column": "string", 
      "fitted_schema": "string",
      "explanation": "string"
    }
  ],
  "status": "completed"
}
```

### Benchmark Routes

#### POST /benchmark
Run benchmark for the n8n pipeline across all environment directories.

**Parameters (form data):**
- `pipeline_name` (string, required): Name to save in the database for this benchmark run
- `pipeline_route` (string, required): The route to use for the n8n pipeline
- `use_mock` (boolean, optional): If True, use mock provider instead of real n8n (default: False)

**Response:**
```json
{
  "status": "success",
  "message": "string"
}
```

#### GET /benchmark
Get benchmark results for all pipelines in the database.

**Response:**
```json
{
  "results": {
    "pipeline_name": {
      "accuracy": 0.0,
      "schema_accuracy": 0.0,
      "column_accuracy": 0.0,
      "env_accuracy": 0.0,
      "nothing_compatible_accuracy": 0.0,
      "total_tests": 0,
      "wrong_matches": [],
      "correct_matches": [],
      "total_predictions": 0
    }
  }
}
```

#### GET /benchmark/{pipeline_name}
Get benchmark results for a specific pipeline.

**Parameters:**
- `pipeline_name` (string, required): Name of the pipeline to get results for

**Response:**
```json
{
  "pipeline_name": "string",
  "results": {
    "accuracy": 0.0,
    "schema_accuracy": 0.0,
    "column_accuracy": 0.0,
    "env_accuracy": 0.0,
    "nothing_compatible_accuracy": 0.0,
    "total_tests": 0,
    "wrong_matches": [],
    "total_predictions": 0
  }
}
```

### Database Routes

#### GET /db/pipeline_results
Get pipeline results from the database.

**Query Parameters:**
- `pipeline_name` (string, optional): Filter results by pipeline name
- `include_wrong_matches` (boolean, optional): Compare with ground truth to identify wrong matches (default: False)
- `limit` (integer, optional): Maximum number of results to return (default: 100)

**Response:**
```json
{
  "status": "success",
  "pipeline_name": "string",
  "results_count": 0,
  "results": [],
  "wrong_matches": [],
  "wrong_matches_count": 0
}
```

### Utility Routes

#### GET /db/status
Check database connection status.

**Response:**
```json
{
  "status": "connected",
  "message": "Successfully connected to PostgreSQL database"
}
```

#### DELETE /db/clear
Clear all data from database tables (requires confirmation).

**Query Parameters:**
- `confirm` (string): Must be "true" to confirm the action

**Response:**
```json
{
  "status": "success",
  "message": "string"
}
```

#### GET /
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "service": "Kimestry-Benchmark API"
}
```

## Error Handling

All endpoints return appropriate HTTP status codes:
- `200`: Success
- `400`: Bad request (invalid parameters)
- `404`: Resource not found
- `500`: Internal server error

Error responses include a details field with more information about the error.

## Environment Variables

The application uses the following environment variables:
- `POSTGRES_CONNECTION_STRING`: PostgreSQL connection string (default: `postgresql://user:password@localhost:5433/kimestry`)
- `MICK_API_BASE_URL`: Base URL for Mick API (default: `http://localhost:8080/api`)
- `EXCEL_FILES_DIR`: Directory for Excel files (default: `./data/excels`)
- `GROUND_TRUTH_DIR`: Directory for ground truth data (default: `./data/ground_truth`)
- `RESULTS_DIR`: Directory for results (default: `./data/results`)
- `N8N_URL`: URL for n8n webhook (default: `https://ronihabaishan.app.n8n.cloud/webhook/schema-matching`)