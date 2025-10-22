from typing import List, Dict, Any
from src.utils.models import MatchResultsModel
from src.providers.postgress import postgres_provider
from src.utils.logging_setup import get_logger
from src.utils.func_utils import load_json
from src.utils.constants import GROUND_TRUTH_DIR
import os
from pathlib import Path

logger = get_logger(__name__)


def calculate_accuracy(predicted: MatchResultsModel, expected: MatchResultsModel) -> float:
    """
    Calculate accuracy score for a single prediction against expected result
    Returns 1.0 if perfect match, 0.0 otherwise
    """
    if (predicted.fitted_column == expected.fitted_column and 
        predicted.fitted_schema == expected.fitted_schema):
        return 1.0
    return 0.0


def calculate_schema_accuracy(predicted: MatchResultsModel, expected: MatchResultsModel) -> float:
    """
    Calculate schema accuracy - whether the schema was correctly identified
    """
    if predicted.fitted_schema == expected.fitted_schema:
        return 1.0
    return 0.0


def calculate_column_accuracy(predicted: MatchResultsModel, expected: MatchResultsModel) -> float:
    """
    Calculate column accuracy - whether the column was correctly identified
    """
    if predicted.fitted_column == expected.fitted_column:
        return 1.0
    return 0.0


def calculate_nothing_compatible_accuracy(predicted: MatchResultsModel, expected: MatchResultsModel) -> float:
    """
    Calculate accuracy for "nothing compatible" cases
    """
    pred_nothing = not predicted.fitted_column and not predicted.fitted_schema
    exp_nothing = not expected.fitted_column and not expected.fitted_schema
    
    if pred_nothing and exp_nothing:
        return 1.0  # Both predicted and expected "nothing compatible"
    elif not pred_nothing and not exp_nothing:
        return 1.0  # Both predicted and expected a match
    elif pred_nothing and not exp_nothing:
        return 0.0  # Predicted nothing but there was a match
    elif not pred_nothing and exp_nothing:
        return 0.0  # Predicted a match but there was nothing compatible
    return 0.0


def calculate_metrics_for_results(results: List[Dict[str, Any]], ground_truth: List[MatchResultsModel]) -> Dict[str, float]:
    """
    Calculate metrics for a set of results against ground truth - keeping only column+schema accuracy and schema accuracy
    """
    if not results or not ground_truth:
        return {
            "accuracy": 0.0,  # This is column+schema accuracy
            "schema_accuracy": 0.0
        }
    
    total_predictions = len(results)
    accuracy_count = 0  # This is column+schema accuracy
    schema_accuracy_count = 0
    
    # Create a mapping of original columns to ground truth for easier lookup
    gt_mapping = {}
    for gt in ground_truth:
        gt_mapping[gt.original_column] = gt
    
    for result_entry in results:
        result = result_entry['result'] if isinstance(result_entry['result'], MatchResultsModel) else result_entry['result']
        original_column = result.original_column
        
        # Find corresponding ground truth
        if original_column in gt_mapping:
            expected = gt_mapping[original_column]
            
            # Calculate individual accuracies
            accuracy_count += calculate_accuracy(result, expected)  # Column+schema accuracy
            schema_accuracy_count += calculate_schema_accuracy(result, expected)
    
    # Calculate percentages
    metrics = {
        "accuracy": accuracy_count / total_predictions if total_predictions > 0 else 0.0,  # Column+schema accuracy
        "schema_accuracy": schema_accuracy_count / total_predictions if total_predictions > 0 else 0.0
    }
    
    return metrics


def calculate_env_accuracy_by_job_and_env(results_by_job: Dict[str, Dict]) -> Dict[str, Dict[str, float]]:
    """
    Calculate column+schema accuracy and schema accuracy for each environment by grouping results by environment
    """
    env_metrics = {}
    
    # Group all results by environment
    env_results = {}
    for job_id, job_data in results_by_job.items():
        env_id = job_data['env_id']
        predictions = job_data['predictions']
        
        if env_id not in env_results:
            env_results[env_id] = []
        
        env_results[env_id].extend(predictions)
    
    # Calculate accuracy for each environment
    for env_id, predictions in env_results.items():
        # Let's recalculate using a different approach - we need to get ground truth for each environment
        # by going through the individual jobs and getting ground truth for each table
        per_env_correct = 0
        per_env_total = 0
        
        # For each job in this environment, find its ground truth and calculate accuracy
        for job_id, job_data in results_by_job.items():
            if job_data['env_id'] == env_id:
                table_name = job_data['table_name']
                predictions = job_data['predictions']
                
                # Load ground truth for this specific table
                gt_file_path = os.path.join(GROUND_TRUTH_DIR, f"{table_name}_gt.json")
                if os.path.exists(gt_file_path):
                    try:
                        gt_data = load_json(gt_file_path)
                        ground_truth = [MatchResultsModel(**item) for item in gt_data]
                        
                        # Create a mapping of original columns to ground truth
                        gt_mapping = {gt.original_column: gt for gt in ground_truth}
                        
                        # Calculate accuracy for this table's predictions
                        for prediction in predictions:
                            original_column = prediction.original_column
                            
                            if original_column in gt_mapping:
                                expected = gt_mapping[original_column]
                                if (prediction.fitted_column == expected.fitted_column and 
                                    prediction.fitted_schema == expected.fitted_schema):
                                    per_env_correct += 1
                                per_env_total += 1
                    except Exception as e:
                        logger.error(f"Error processing ground truth for table {table_name} in env {env_id}: {str(e)}")
                        continue
                else:
                    logger.warning(f"Ground truth file not found for table {table_name} in env {env_id}: {gt_file_path}")
                    continue
        
        # Calculate environment accuracy (column+schema accuracy)
        env_accuracy = per_env_correct / per_env_total if per_env_total > 0 else 0.0
        
        # Calculate schema accuracy for this env
        schema_correct = 0
        
        for job_id, job_data in results_by_job.items():
            if job_data['env_id'] == env_id:
                table_name = job_data['table_name']
                predictions = job_data['predictions']
                
                gt_file_path = os.path.join(GROUND_TRUTH_DIR, f"{table_name}_gt.json")
                if os.path.exists(gt_file_path):
                    try:
                        gt_data = load_json(gt_file_path)
                        ground_truth = [MatchResultsModel(**item) for item in gt_data]
                        
                        # Create a mapping of original columns to ground truth
                        gt_mapping = {gt.original_column: gt for gt in ground_truth}
                        
                        # Calculate schema accuracy for this table's predictions
                        for prediction in predictions:
                            original_column = prediction.original_column
                            
                            if original_column in gt_mapping:
                                expected = gt_mapping[original_column]
                                
                                # Schema accuracy
                                if prediction.fitted_schema == expected.fitted_schema:
                                    schema_correct += 1
                    except Exception as e:
                        logger.error(f"Error processing ground truth for schema calc for table {table_name} in env {env_id}: {str(e)}")
                        continue
        
        env_metrics[env_id] = {
            "accuracy": env_accuracy,  # This is column+schema accuracy
            "schema_accuracy": schema_correct / per_env_total if per_env_total > 0 else 0.0,
            "total_tests": per_env_total
        }
    
    return env_metrics


def calculate_pipeline_statistics_with_wrong_matches(pipeline_name: str):
    """
    Calculate statistics for a pipeline by comparing database results with ground truth
    Additionally returns wrong matches for analysis - keeping only column+schema accuracy and schema accuracy
    """
    # Use a try-finally block to ensure the database connection is always closed
    postgres_provider.connect()
    
    try:
        logger.info(f"Calculating statistics with wrong matches for pipeline: {pipeline_name}")
        
        # Get all pipeline results for the specified pipeline
        with postgres_provider.connection.cursor() as cursor:
            cursor.execute("""
                SELECT job_id, table_name, pipeline_name, env_id, original_column, 
                       fitted_column, fitted_schema, explanation
                FROM pipeline_results 
                WHERE pipeline_name = %s
                ORDER BY job_id, timestamp
            """, (pipeline_name,))
            db_results = cursor.fetchall()
        
        if not db_results:
            logger.warning(f"No pipeline results found in database for pipeline: {pipeline_name}")
            return {
                "accuracy": 0.0,  # This is column+schema accuracy
                "schema_accuracy": 0.0,
                "total_tests": 0,
                "wrong_matches": []
            }
        
        # Group results by job_id and table_name to process each table separately
        results_by_job = {}
        for row in db_results:
            job_id, table_name, pipeline_name_db, env_id, original_column, fitted_column, fitted_schema, explanation = row
            
            if job_id not in results_by_job:
                results_by_job[job_id] = {
                    'table_name': table_name,
                    'env_id': env_id,
                    'predictions': []
                }
            
            # Create MatchResultsModel from database result
            result = MatchResultsModel(
                original_column=original_column,
                fitted_column=fitted_column,
                fitted_schema=fitted_schema,
                explanation=explanation
            )
            results_by_job[job_id]['predictions'].append(result)
        
        # Calculate overall metrics across all jobs and collect wrong matches only
        total_predictions = 0
        total_accuracy = 0.0  # This is column+schema accuracy
        total_schema_accuracy = 0.0
        all_wrong_matches = []
        
        # For each job, find the corresponding ground truth and calculate metrics
        for job_id, job_data in results_by_job.items():
            table_name = job_data['table_name']
            predictions = job_data['predictions']
            
            # Load ground truth for this table
            gt_file_path = os.path.join(GROUND_TRUTH_DIR, f"{table_name}_gt.json")
            if os.path.exists(gt_file_path):
                try:
                    gt_data = load_json(gt_file_path)
                    ground_truth = [MatchResultsModel(**item) for item in gt_data]
                    
                    # Create a mapping of original columns to ground truth for easier lookup
                    gt_mapping = {}
                    for gt in ground_truth:
                        gt_mapping[gt.original_column] = gt
                    
                    # Process each prediction against ground truth
                    for prediction in predictions:
                        original_column = prediction.original_column
                        total_predictions += 1
                        
                        if original_column in gt_mapping:
                            expected = gt_mapping[original_column]
                            
                            # Check for correct match
                            is_correct = (prediction.fitted_column == expected.fitted_column and 
                                         prediction.fitted_schema == expected.fitted_schema)
                            
                            # Only add to wrong matches if it's incorrect
                            if not is_correct:
                                wrong_match = {
                                    'job_id': job_id,
                                    'table_name': table_name,
                                    'env_id': job_data['env_id'],
                                    'original_column': original_column,
                                    'predicted_fitted_column': prediction.fitted_column,
                                    'predicted_fitted_schema': prediction.fitted_schema,
                                    'expected_fitted_column': expected.fitted_column,
                                    'expected_fitted_schema': expected.fitted_schema,
                                    'explanation': prediction.explanation
                                }
                                all_wrong_matches.append(wrong_match)
                            
                            # Accumulate metrics
                            total_accuracy += 1.0 if is_correct else 0.0
                            total_schema_accuracy += 1.0 if prediction.fitted_schema == expected.fitted_schema else 0.0
                except Exception as e:
                    logger.error(f"Error processing ground truth for {table_name}: {str(e)}")
                    continue
            else:
                logger.warning(f"Ground truth file not found for {table_name}: {gt_file_path}")
                continue
        
        # Calculate final averages
        if total_predictions > 0:
            final_metrics = {
                "accuracy": total_accuracy / total_predictions,  # Column+schema accuracy
                "schema_accuracy": total_schema_accuracy / total_predictions,
                "total_tests": total_predictions
            }
        else:
            final_metrics = {
                "accuracy": 0.0,
                "schema_accuracy": 0.0,
                "total_tests": 0
            }
        
        # Calculate environment-specific accuracy
        env_metrics = calculate_env_accuracy_by_job_and_env(results_by_job)
        
        # Calculate overall environment accuracy as average of all env accuracies
        if env_metrics:
            total_env_accuracy = sum(env_data['accuracy'] for env_data in env_metrics.values())
            # Note: We don't include env_accuracy in the returned metrics as per the requirement
            
            # Save environment-specific metrics to the new table
            import uuid
            from datetime import datetime
            benchmark_run_id = f"benchmark_{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"
            
            for env_id, env_data in env_metrics.items():
                postgres_provider.save_env_benchmark_results(
                    benchmark_run_id=benchmark_run_id,
                    pipeline_name=pipeline_name,
                    env_id=env_id,
                    metrics={
                        'accuracy': env_data['accuracy'],
                        'schema_accuracy': env_data['schema_accuracy'],
                        'column_accuracy': env_data['column_accuracy'],
                        'nothing_compatible_accuracy': 0.0  # Placeholder
                    },
                    total_tests=env_data['total_tests']
                )
        
        # Also save to benchmark results table for historical tracking
        try:
            import uuid
            from datetime import datetime
            benchmark_run_id = f"benchmark_{pipeline_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4()}"
            
            postgres_provider.save_benchmark_results(
                benchmark_run_id=benchmark_run_id,
                pipeline_name=pipeline_name,
                metrics=final_metrics,
                total_tests=final_metrics['total_tests']
            )
        except Exception as e:
            logger.error(f"Error saving benchmark results: {str(e)}")
        
        logger.info(f"Calculated statistics with wrong matches for pipeline: {pipeline_name}")
        
        # Return metrics and only wrong matches
        final_metrics['wrong_matches'] = all_wrong_matches
        final_metrics['total_predictions'] = total_predictions
        return final_metrics
        
    except Exception as e:
        logger.error(f"Error calculating statistics for pipeline {pipeline_name}: {str(e)}")
        # Re-raise the exception to properly propagate errors
        raise
    finally:
        # Always disconnect from the database, even if there's an exception
        try:
            postgres_provider.disconnect()
        except:
            # If disconnect fails, log it but don't raise another exception
            logger.warning("Could not disconnect from database in finally block")


def calculate_pipeline_statistics(pipeline_name: str) -> Dict[str, float]:
    """
    Calculate statistics for a pipeline by comparing database results with ground truth
    Wrapper function that returns only the metrics (for backward compatibility)
    """
    result = calculate_pipeline_statistics_with_wrong_matches(pipeline_name)
    # Return only the metrics without wrong matches for backward compatibility
    filtered_result = {k: v for k, v in result.items() if k != 'wrong_matches' and k != 'total_predictions'}
    return filtered_result


def get_pipeline_statistics(pipeline_name: str) -> Dict[str, float]:
    """
    Query results after running benchmarks on a pipeline.
    Calculate statistics by comparing database results with ground truth.
    """
    # This now calls the calculation function instead of just retrieving saved results
    return calculate_pipeline_statistics(pipeline_name)


def get_all_pipeline_statistics_with_wrong_matches() -> Dict[str, Dict]:
    """
    Get statistics with wrong matches for all pipelines by comparing database results with ground truth.
    """
    # Use a try-finally block to ensure the database connection is always closed
    postgres_provider.connect()
    
    try:
        logger.info("Getting statistics with wrong matches for all pipelines")
        
        with postgres_provider.connection.cursor() as cursor:
            cursor.execute("SELECT DISTINCT pipeline_name FROM pipeline_results")
            db_pipeline_names = [row[0] for row in cursor.fetchall()]
        
        logger.info(f"Found {len(db_pipeline_names)} distinct pipeline names in database: {db_pipeline_names}")
        
        all_stats = {}
        for pipeline_name in db_pipeline_names:
            stats = calculate_pipeline_statistics_with_wrong_matches(pipeline_name)
            if stats:  # Only add if we have results
                all_stats[pipeline_name] = stats
        
        logger.info(f"Retrieved statistics with wrong matches for {len(all_stats)} pipelines")
        return all_stats
        
    except Exception as e:
        logger.error(f"Error getting statistics with wrong matches for all pipelines: {str(e)}")
        return {}
    finally:
        # Always disconnect from the database, even if there's an exception
        try:
            postgres_provider.disconnect()
        except:
            # If disconnect fails, log it but don't raise another exception
            logger.warning("Could not disconnect from database in finally block")


def get_all_pipeline_statistics() -> Dict[str, Dict[str, float]]:
    """
    Get statistics for all pipelines by comparing database results with ground truth.
    """
    try:
        logger.info("Getting statistics for all pipelines")
        
        # For this function, we would typically query all benchmark results
        # Since we need all pipeline names, we'll get them from a list of known pipelines
        from src.utils.constants import PIPELINE_TYPES
        
        all_stats = {}
        for pipeline_name in PIPELINE_TYPES:
            stats = calculate_pipeline_statistics(pipeline_name)  # This returns only metrics (backward compatibility)
            if stats:  # Only add if we have results
                all_stats[pipeline_name] = stats
        
        logger.info(f"Retrieved statistics for {len(all_stats)} pipelines")
        return all_stats
        
    except Exception as e:
        logger.error(f"Error getting statistics for all pipelines: {str(e)}")
        return {}


def get_all_pipeline_env_statistics() -> Dict[str, Dict[str, Dict[str, float]]]:
    """
    Get environment-specific statistics for all pipelines.
    Returns a nested dictionary: {pipeline_name: {env_id: {metric: value}}}
    """
    try:
        logger.info("Getting environment-specific statistics for all pipelines")
        
        from src.utils.constants import PIPELINE_TYPES
        from src.providers.postgress import postgres_provider
        
        all_env_stats = {}
        
        # Connect to database
        postgres_provider.connect()
        
        for pipeline_name in PIPELINE_TYPES:
            # Get all environment-specific benchmark results for this pipeline
            env_results = postgres_provider.get_env_benchmark_results(pipeline_name)
            
            if env_results:
                # Group results by environment
                env_stats = {}
                for result in env_results:
                    env_id = result['env_id']
                    if env_id not in env_stats:
                        env_stats[env_id] = []
                    env_stats[env_id].append(result)
                
                # Take the most recent result for each environment
                recent_env_stats = {}
                for env_id, results in env_stats.items():
                    # Sort by timestamp and take the most recent
                    most_recent = max(results, key=lambda x: x['timestamp'])
                    recent_env_stats[env_id] = {
                        'accuracy': float(most_recent['accuracy']) if most_recent['accuracy'] is not None else 0.0,
                        'schema_accuracy': float(most_recent['schema_accuracy']) if most_recent['schema_accuracy'] is not None else 0.0,
                        'total_tests': most_recent['total_tests'] if most_recent['total_tests'] is not None else 0,
                        'timestamp': most_recent['timestamp']
                    }
                
                if recent_env_stats:
                    all_env_stats[pipeline_name] = recent_env_stats
        
        postgres_provider.disconnect()
        
        logger.info(f"Retrieved environment-specific statistics for {len(all_env_stats)} pipelines")
        return all_env_stats
        
    except Exception as e:
        logger.error(f"Error getting environment-specific statistics for all pipelines: {str(e)}")
        if 'postgres_provider' in locals() or 'postgres_provider' in globals():
            from src.providers.postgress import postgres_provider
            if postgres_provider.connection:
                postgres_provider.disconnect()
        return {}