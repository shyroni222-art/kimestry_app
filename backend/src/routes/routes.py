from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional
import pandas as pd
import uuid
from pathlib import Path
from psycopg2.extras import RealDictCursor

from src.benchmarking.benchmark import benchmark
from src.benchmarking.pipeline_statisics import get_pipeline_statistics, get_all_pipeline_statistics
from src.pipeline.pipelines.n8n_pipeline import N8NPipeline
from src.utils.func_utils import load_excel_file
from src.utils.constants import EXCEL_FILES_DIR
from src.utils.logging_setup import get_logger
from src.providers.postgress import postgres_provider
from src.providers.mick import get_database_schema

logger = get_logger(__name__)
router = APIRouter()


@router.post("/benchmark")
async def run_benchmark(pipeline_name: str = Form(...), pipeline_route: str = Form(...), use_mock: bool = Form(False), timeout: int = Form(600)):
    """
    Run benchmark for the n8n pipeline across all environment directories in data/excels/
    The pipeline_name parameter will be used as the name saved in the database
    The pipeline_route parameter specifies which route to use for the n8n pipeline
    The timeout parameter specifies the timeout in seconds (default 600 seconds = 10 minutes)
    
    Args:
        pipeline_name (str): Name to save in the database for this pipeline run
        pipeline_route (str): The route to use for the n8n pipeline
        use_mock (bool, optional): If True, use mock provider instead of real n8n. Defaults to False.
        timeout (int, optional): Timeout in seconds for pipeline execution. Defaults to 600 (10 minutes).
    """
    try:
        # Import the benchmark function here to avoid circular import issues
        from src.benchmarking.benchmark import benchmark
        
        # Set up the provider to use based on the use_mock flag
        if use_mock:
            from src.providers.n8n_mock import mock_n8n_provider
            from src.providers import n8n
            # Temporarily replace the n8n provider with mock
            original_provider = n8n.n8n_provider
            # Update the mock provider to use the custom route if available
            n8n.n8n_provider = mock_n8n_provider
            logger.info("Using mock n8n provider for benchmark")
        else:
            from src.providers import n8n
            # We need to temporarily update n8n provider to use the custom route
            original_n8n_route = n8n.n8n_provider.n8n_base_url
            # Don't change the global n8n URL directly, instead modify how the benchmark uses pipelines
            logger.info(f"Running benchmark using route: {pipeline_route}")
        
        try:
            # Get all environment directories from data/excels/
            env_base_path = Path(EXCEL_FILES_DIR)
            env_directories = [d for d in env_base_path.iterdir() if d.is_dir()]
            
            if not env_directories:
                # If no environment directories, run with default_env
                benchmark(pipeline_name, "default_env", n8n_route=pipeline_route, timeout=timeout)
            else:
                # Run benchmark for each environment directory
                for env_dir in env_directories:
                    env_id_from_dir = env_dir.name  # Use folder name as env_id
                    excel_files = list(env_dir.glob("*.xlsx")) + list(env_dir.glob("*.xls"))
                    
                    if excel_files:
                        logger.info(f"Running benchmark for environment: {env_id_from_dir} with {len(excel_files)} Excel files")
                        # Run benchmark for this specific environment
                        benchmark(pipeline_name, env_id_from_dir, excel_dir=str(env_dir), n8n_route=pipeline_route, timeout=timeout)
                    else:
                        logger.info(f"No Excel files found in environment directory: {env_id_from_dir}")
        
            return {"status": "success", "message": f"{'Mock ' if use_mock else ''}Benchmark completed for pipeline {pipeline_name}"}
        
        finally:
            # Restore the original provider if we used a mock
            if use_mock:
                from src.providers import n8n
                n8n.n8n_provider = original_provider
                logger.info("Restored original n8n provider after benchmark")
            else:
                from src.providers import n8n
                # Restore original route if needed
                logger.info("Completed benchmark run")
    
    except Exception as e:
        logger.error(f"Error running benchmark: {str(e)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/benchmark/{pipeline_name}")
async def get_benchmark_results(pipeline_name: str):
    """
    Get all benchmark results for a specific pipeline
    """
    try:
        from src.benchmarking.pipeline_statisics import calculate_pipeline_statistics_with_wrong_matches
        results = calculate_pipeline_statistics_with_wrong_matches(pipeline_name)
        if not results:
            raise HTTPException(status_code=404, detail=f"No benchmark results found for pipeline {pipeline_name}")
        
        return {"pipeline_name": pipeline_name, "results": results}
    
    except Exception as e:
        logger.error(f"Error getting benchmark results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))





@router.get("/benchmark")
async def get_all_benchmark_results():
    """
    Get benchmark results for all pipelines
    """
    try:
        from src.benchmarking.pipeline_statisics import get_all_pipeline_statistics_with_wrong_matches
        results = get_all_pipeline_statistics_with_wrong_matches()
        return {"results": results}
    
    except Exception as e:
        logger.error(f"Error getting all benchmark results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))





@router.post("/pipeline/run")
async def run_pipeline(
    file: UploadFile = File(...),
    pipeline_name: str = Form(...),  # The name to save in the database for this pipeline run
    env_id: str = Form("default_env"),
    pipeline_route: str = Form(...),  # The route to use for the n8n pipeline
    timeout: int = Form(600)  # Timeout in seconds for pipeline execution (default 600 seconds = 10 minutes)
):
    """
    Run the n8n pipeline on an uploaded Excel file using the specified route
    The pipeline_name parameter will be the name saved in the database
    The timeout parameter specifies the timeout in seconds (default 600 seconds = 10 minutes)
    """
    try:
        # Create a temporary file to save the uploaded Excel file
        file_id = str(uuid.uuid4())
        file_path = f"{EXCEL_FILES_DIR}/{file_id}_{file.filename}"
        
        # Ensure the directory exists
        import os
        os.makedirs(EXCEL_FILES_DIR, exist_ok=True)
        
        # Save the uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        try:
            # Load the Excel file
            table_df = load_excel_file(file_path)
            
            # Fetch the database schema for the environment
            env_schema = get_database_schema(env_id)
            
            # Always use the n8n pipeline but with the custom name, route, and timeout
            pipeline = N8NPipeline(name=pipeline_name, job_id=file_id, n8n_route=pipeline_route, timeout=timeout)
            
            results = pipeline.run(env_id, table_df, env_schema)
            
            # Format results for response
            formatted_results = []
            for result in results:
                formatted_results.append({
                    "original_column": result.original_column,
                    "fitted_column": result.fitted_column,
                    "fitted_schema": result.fitted_schema,
                    "explanation": result.explanation
                })
                
                # Save result to PostgreSQL using the custom name provided by user
                try:
                    table_name = file.filename if file.filename else f"table_{file_id}"
                    # Remove file extension from table name
                    if '.' in table_name:
                        table_name = table_name.rsplit('.', 1)[0]
                    
                    postgres_provider.save_pipeline_result(
                        job_id=file_id,
                        table_name=table_name,
                        pipeline_name=pipeline_name,  # Use the name provided by the user
                        env_id=env_id,
                        result=result
                    )
                except Exception as e:
                    logger.error(f"Failed to save pipeline result to PostgreSQL: {str(e)}")
                    # Continue with the response even if saving to PostgreSQL fails
            
            return {
                "job_id": file_id,
                "pipeline_name": pipeline_name,  # Return the custom name provided by user
                "env_id": env_id,
                "results": formatted_results,
                "status": "completed"
            }
            
        finally:
            # Clean up the temporary file
            import os
            if os.path.exists(file_path):
                os.remove(file_path)
    
    except Exception as e:
        logger.error(f"Error running pipeline: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy", "service": "Kimestry API"}

@router.get("/db/status")
async def db_status():
    """
    Check database connection status
    """
    try:
        # Test database connection by attempting a simple query
        with postgres_provider.connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
        
        return {
            "status": "connected",
            "message": "Successfully connected to PostgreSQL database"
        }
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Database connection failed: {str(e)}")

@router.get("/db/pipeline_results")
async def get_pipeline_results(pipeline_name: Optional[str] = None, include_wrong_matches: bool = False, limit: int = 100):
    """
    Get pipeline results from the database
    If pipeline_name is provided, returns all results for that pipeline
    If no pipeline_name is provided, returns the most recent pipeline results
    If include_wrong_matches is True, compares results with ground truth to identify wrong matches
    """
    try:
        if pipeline_name:
            # Get results for a specific pipeline
            results = postgres_provider.get_pipeline_results_by_pipeline_name(pipeline_name, limit)
        else:
            # Get the most recent pipeline results
            with postgres_provider.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM pipeline_results ORDER BY timestamp DESC LIMIT %s
                """, (limit,))
                results = [dict(row) for row in cursor.fetchall()]
        
        response = {
            "status": "success",
            "pipeline_name": pipeline_name if pipeline_name else "all_pipelines",
            "results_count": len(results),
            "results": results
        }
        
        # If include_wrong_matches is True, compare with ground truth to identify wrong matches
        if include_wrong_matches and results:
            from src.utils.func_utils import load_json
            from src.utils.models import MatchResultsModel
            from src.utils.constants import GROUND_TRUTH_DIR
            import os
            from pathlib import Path
            
            # Group results by table_name to match with ground truth
            results_by_table = {}
            for result in results:
                table_name = result['table_name']
                if table_name not in results_by_table:
                    results_by_table[table_name] = []
                results_by_table[table_name].append(result)
            
            all_wrong_matches = []
            
            # For each table, compare with ground truth
            for table_name, table_results in results_by_table.items():
                gt_file_path = os.path.join(GROUND_TRUTH_DIR, f"{table_name}_gt.json")
                if os.path.exists(gt_file_path):
                    try:
                        gt_data = load_json(gt_file_path)
                        ground_truth = [MatchResultsModel(**item) for item in gt_data]
                        
                        # Create a mapping of original columns to ground truth
                        gt_mapping = {gt.original_column: gt for gt in ground_truth}
                        
                        # Compare each result with ground truth
                        for result in table_results:
                            original_column = result['original_column']
                            if original_column in gt_mapping:
                                expected = gt_mapping[original_column]
                                # Check if the prediction is wrong
                                is_correct = (result['fitted_column'] == expected.fitted_column and 
                                            result['fitted_schema'] == expected.fitted_schema)
                                if not is_correct:
                                    wrong_match = {
                                        'job_id': result['job_id'],
                                        'table_name': result['table_name'],
                                        'env_id': result['env_id'],
                                        'original_column': original_column,
                                        'predicted_fitted_column': result['fitted_column'],
                                        'predicted_fitted_schema': result['fitted_schema'],
                                        'expected_fitted_column': expected.fitted_column,
                                        'expected_fitted_schema': expected.fitted_schema,
                                        'explanation': result['explanation']
                                    }
                                    all_wrong_matches.append(wrong_match)
                    except Exception as e:
                        logger.error(f"Error processing ground truth for {table_name}: {str(e)}")
                        continue
            
            response["wrong_matches"] = all_wrong_matches
            response["wrong_matches_count"] = len(all_wrong_matches)
        
        return response
    except Exception as e:
        logger.error(f"Error getting pipeline results: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))



@router.delete("/db/clear")
async def clear_database(confirm: str = "false"):
    """
    Clear all data from database tables - requires confirmation
    """
    if confirm.lower() != "true":
        return {
            "status": "error",
            "message": "This action requires confirmation. Add ?confirm=true to the query"
        }
    
    try:
        with postgres_provider.connection.cursor() as cursor:
            # Clear the pipeline results table
            cursor.execute("DELETE FROM pipeline_results;")
            pipeline_deleted = cursor.rowcount

            # Clear the benchmark results table  
            cursor.execute("DELETE FROM benchmark_results;")
            benchmark_deleted = cursor.rowcount
            
            postgres_provider.connection.commit()
        
        logger.info(f"Cleared {pipeline_deleted} pipeline results and {benchmark_deleted} benchmark results")
        return {
            "status": "success",
            "message": f"Cleared {pipeline_deleted} pipeline results and {benchmark_deleted} benchmark results"
        }
    except Exception as e:
        logger.error(f"Error clearing database: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))