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

def calculate_pipeline_statistics_with_wrong_matches(pipeline_name: str):
    """
    Calculate statistics for a pipeline by comparing database results with ground truth
    Returns only: column+schema accuracy, schema accuracy, and wrong matches
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
                "wrong_matches": []
            }
        
        # Calculate overall metrics across all jobs and collect wrong matches only
        total_predictions = 0
        total_accuracy = 0.0  # This is column+schema accuracy
        total_schema_accuracy = 0.0
        all_wrong_matches = []
        
        # Process each prediction against ground truth
        for row in db_results:
            job_id, table_name, pipeline_name_db, env_id, original_column, fitted_column, fitted_schema, explanation = row
            
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
                    
                    # Create MatchResultsModel from database result
                    prediction = MatchResultsModel(
                        original_column=original_column,
                        fitted_column=fitted_column,
                        fitted_schema=fitted_schema,
                        explanation=explanation
                    )
                    
                    # Process prediction against ground truth
                    if original_column in gt_mapping:
                        expected = gt_mapping[original_column]
                        
                        # Check for correct match (add explicit string conversion to handle potential type mismatches)
                        pred_fitted_col = str(prediction.fitted_column) if prediction.fitted_column is not None else ""
                        pred_fitted_schema = str(prediction.fitted_schema) if prediction.fitted_schema is not None else ""
                        exp_fitted_col = str(expected.fitted_column) if expected.fitted_column is not None else ""
                        exp_fitted_schema = str(expected.fitted_schema) if expected.fitted_schema is not None else ""
                        
                        # Check for correct match
                        is_correct = (pred_fitted_col == exp_fitted_col and 
                                     pred_fitted_schema == exp_fitted_schema)
                        
                        # Only add to wrong matches if it's incorrect
                        if not is_correct:
                            wrong_match = {
                                'job_id': job_id,
                                'table_name': table_name,
                                'env_id': env_id,
                                'original_column': original_column,
                                'predicted_fitted_column': pred_fitted_col,
                                'predicted_fitted_schema': pred_fitted_schema,
                                'expected_fitted_column': exp_fitted_col,
                                'expected_fitted_schema': exp_fitted_schema,
                                'explanation': prediction.explanation
                            }
                            all_wrong_matches.append(wrong_match)
                        
                        # Accumulate metrics
                        total_predictions += 1
                        total_accuracy += 1.0 if is_correct else 0.0
                        total_schema_accuracy += 1.0 if pred_fitted_schema == exp_fitted_schema else 0.0
                    else:
                        logger.debug(f"Original column '{original_column}' not found in ground truth mapping for table '{table_name}'")
                        # Still count this as an incorrect prediction since no ground truth exists for this column
                        total_predictions += 1
                        # Both accuracies remain at 0.0 for this entry
                        wrong_match = {
                            'job_id': job_id,
                            'table_name': table_name,
                            'env_id': env_id,
                            'original_column': original_column,
                            'predicted_fitted_column': str(fitted_column) if fitted_column is not None else "",
                            'predicted_fitted_schema': str(fitted_schema) if fitted_schema is not None else "",
                            'expected_fitted_column': "NOT_FOUND",
                            'expected_fitted_schema': "NOT_FOUND",
                            'explanation': prediction.explanation if 'prediction' in locals() else explanation
                        }
                        all_wrong_matches.append(wrong_match)
                        
                except Exception as e:
                    logger.error(f"Error processing ground truth for {table_name}: {str(e)}")
                    continue
            else:
                logger.warning(f"Ground truth file not found for {table_name}: {gt_file_path}")
                # If ground truth file doesn't exist, we can't evaluate accuracy, so skip
                continue
        
        # Calculate final averages
        if total_predictions > 0:
            final_metrics = {
                "accuracy": total_accuracy / total_predictions,  # Column+schema accuracy
                "schema_accuracy": total_schema_accuracy / total_predictions,
            }
        else:
            final_metrics = {
                "accuracy": 0.0,
                "schema_accuracy": 0.0,
            }
        
        # Return only the required 3 metrics
        final_metrics['wrong_matches'] = all_wrong_matches
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


def get_pipeline_statistics(pipeline_name: str) -> Dict[str, float]:
    """
    Query results after running benchmarks on a pipeline.
    Calculate statistics by comparing database results with ground truth.
    Returns only: column+schema accuracy, schema accuracy, and wrong matches
    """
    return calculate_pipeline_statistics_with_wrong_matches(pipeline_name)


def calculate_metrics_for_results(predicted_results: List[MatchResultsModel], expected_results: List[MatchResultsModel]) -> Dict[str, float]:
    """
    Calculate metrics for a list of predicted results compared to expected results
    """
    if len(predicted_results) != len(expected_results):
        logger.warning(f"Length mismatch between predicted ({len(predicted_results)}) and expected ({len(expected_results)}) results")
        # Truncate to the shorter list to avoid index errors
        min_length = min(len(predicted_results), len(expected_results))
        predicted_results = predicted_results[:min_length]
        expected_results = expected_results[:min_length]
    
    if not predicted_results:
        return {
            "accuracy": 0.0,
            "schema_accuracy": 0.0,
            "total_predictions": 0
        }
    
    total_predictions = len(predicted_results)
    total_accuracy = 0.0  # This is column+schema accuracy
    total_schema_accuracy = 0.0
    
    for predicted, expected in zip(predicted_results, expected_results):
        # Check for correct match (add explicit string conversion to handle potential type mismatches)
        pred_fitted_col = str(predicted.fitted_column) if predicted.fitted_column is not None else ""
        pred_fitted_schema = str(predicted.fitted_schema) if predicted.fitted_schema is not None else ""
        exp_fitted_col = str(expected.fitted_column) if expected.fitted_column is not None else ""
        exp_fitted_schema = str(expected.fitted_schema) if expected.fitted_schema is not None else ""
        
        # Calculate column+schema accuracy
        is_correct = (pred_fitted_col == exp_fitted_col and 
                     pred_fitted_schema == exp_fitted_schema)
        
        total_accuracy += 1.0 if is_correct else 0.0
        total_schema_accuracy += 1.0 if pred_fitted_schema == exp_fitted_schema else 0.0
    
    # Calculate final averages
    final_metrics = {
        "accuracy": total_accuracy / total_predictions if total_predictions > 0 else 0.0,  # Column+schema accuracy
        "schema_accuracy": total_schema_accuracy / total_predictions if total_predictions > 0 else 0.0,
        "total_predictions": total_predictions
    }
    
    return final_metrics


def get_all_pipeline_statistics_with_wrong_matches() -> Dict[str, Dict]:
    """
    Get statistics with wrong matches for all pipelines by comparing database results with ground truth.
    Returns only: column+schema accuracy, schema accuracy, and wrong matches for each pipeline
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