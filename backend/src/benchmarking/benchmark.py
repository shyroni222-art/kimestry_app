import os
from typing import List
import pandas as pd
from pathlib import Path

from src.utils.models import MatchResultsModel
from src.utils.constants import EXCEL_FILES_DIR, GROUND_TRUTH_DIR, RESULTS_DIR
from src.utils.func_utils import load_excel_file, load_json, create_directory_if_not_exists
from src.providers.postgress import postgres_provider
from src.pipeline.pipelines.n8n_pipeline import N8NPipeline
from src.benchmarking.pipeline_statistics import calculate_metrics_for_results
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


def get_excels_gt(excel_dir: str = None) -> List[MatchResultsModel]:
    """
    Retrieve ground truth Excel file mappings.
    Ground truth files are stored in the GROUND_TRUTH_DIR directory.
    Each Excel file should have a corresponding JSON file with the expected mappings.
    
    Args:
        excel_dir: Directory containing Excel files. If None, uses default EXCEL_FILES_DIR
    """
    ground_truth_mappings = []
    
    # Ensure ground truth directory exists
    create_directory_if_not_exists(GROUND_TRUTH_DIR)
    
    # Determine which directory to look for Excel files in
    target_dir = excel_dir if excel_dir else EXCEL_FILES_DIR
    
    # Look for Excel files and their corresponding ground truth JSON files
    excel_files = [f for f in os.listdir(target_dir) if f.endswith(('.xlsx', '.xls'))]
    
    for excel_file in excel_files:
        base_name = Path(excel_file).stem
        gt_file = os.path.join(GROUND_TRUTH_DIR, f"{base_name}_gt.json")
        
        if os.path.exists(gt_file):
            try:
                gt_data = load_json(gt_file)
                # Convert ground truth data to MatchResultsModel objects
                for item in gt_data:
                    if isinstance(item, dict):
                        match_result = MatchResultsModel(**item)
                        ground_truth_mappings.append(match_result)
            except Exception as e:
                logger.error(f"Error loading ground truth file {gt_file}: {str(e)}")
        else:
            logger.warning(f"Ground truth file not found for {excel_file}: {gt_file}")
    
    return ground_truth_mappings


def benchmark(pipeline_name: str, env_id: str = "default_env", excel_dir: str = None, n8n_route: str = None, timeout: int = 600):
    """
    Accepts a pipeline name, gets the correct pipeline.
    Runs the pipeline on all Excel files in the specified directory.
    Saves the results to PostgreSQL (statistics calculation will be done separately).
    
    Args:
        pipeline_name: Name of the pipeline to run (also used as the name saved in database)
        env_id: Environment ID to use for the pipeline
        excel_dir: Directory containing Excel files to process. If None, uses default EXCEL_FILES_DIR
        n8n_route: The route to use for the n8n pipeline
        timeout: Timeout in seconds for pipeline execution (default 600 seconds = 10 minutes)
    """
    logger.info(f"Starting benchmark for pipeline: {pipeline_name}, environment: {env_id}")
    
    try:
        # Connect to database
        postgres_provider.connect()
        
        # Get the pipeline - create with custom name, route, and timeout
        from src.pipeline.pipelines.n8n_pipeline import N8NPipeline
        pipeline = N8NPipeline(name=pipeline_name, n8n_route=n8n_route, timeout=timeout)
        
        # Determine which directory to process Excel files from
        target_dir = excel_dir if excel_dir else EXCEL_FILES_DIR
        
        # Check if the directory exists
        if not os.path.exists(target_dir):
            logger.warning(f"Directory {target_dir} does not exist")
            return
        
        # Get all Excel files to process from the target directory
        excel_files = [f for f in os.listdir(target_dir) if f.endswith(('.xlsx', '.xls'))]
        
        if not excel_files:
            logger.warning(f"No Excel files found in {target_dir}")
            return
        
        all_results = []
        ground_truth_data = get_excels_gt(excel_dir=target_dir)
        
        # Run pipeline on each Excel file
        for idx, excel_file in enumerate(excel_files):
            logger.info(f"Processing file {idx+1}/{len(excel_files)}: {excel_file}")
            
            file_path = os.path.join(target_dir, excel_file)
            base_name = Path(excel_file).stem
            
            logger.info(f"Processing file: {excel_file} with environment: {env_id}")
            
            try:
                # Load the Excel file
                table_df = load_excel_file(file_path)
                
                # Generate a unique job ID for this run
                job_id = f"benchmark_{pipeline_name}_{env_id}_{base_name}_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}"
                
                # Fetch the database schema for the environment
                from src.providers.mick import get_database_schema
                env_schema = get_database_schema(env_id)
                
                # Run the pipeline with the environment schema
                pipeline.job_id = job_id
                logger.info(f"Starting pipeline execution for job {job_id}")
                
                results = pipeline.run(env_id, table_df, env_schema)
                
                logger.info(f"Pipeline execution completed for job {job_id}, got {len(results)} results")
                
                # Save individual results - derive table_name from the base_name or use a default
                table_name = base_name if base_name else f"benchmark_table_{job_id}"
                for result in results:
                    postgres_provider.save_pipeline_result(job_id, table_name, pipeline_name, env_id, result)
                    all_results.append({
                        'job_id': job_id,
                        'result': result
                    })
                
                logger.info(f"Completed processing {excel_file}, got {len(results)} results")
                
            except Exception as e:
                logger.error(f"Error processing {excel_file} in environment {env_id}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        # Note: Statistics/metrics calculation will be handled separately during statistics retrieval
        # Results are already saved per individual pipeline run in the database
        if all_results:
            logger.info(f"Pipeline processing completed for {pipeline_name} in environment {env_id}. {len(all_results)} results saved to database.")
        else:
            logger.warning(f"No results generated for pipeline {pipeline_name} in environment {env_id}")
        
        # Disconnect from database
        postgres_provider.disconnect()
        
    except Exception as e:
        logger.error(f"Error during benchmark for pipeline {pipeline_name} in environment {env_id}: {str(e)}")
        import traceback
        traceback.print_exc()
        if postgres_provider.connection:
            postgres_provider.disconnect()
        # Re-raise the exception to properly propagate errors
        raise
