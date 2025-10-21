import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Any, Optional
from src.utils.constants import POSTGRES_CONNECTION_STRING
from src.utils.models import MatchResultsModel
from src.utils.logging_setup import get_logger
import json
from datetime import datetime

logger = get_logger(__name__)


class PostgreSQLProvider:
    def __init__(self, connection_string: str = POSTGRES_CONNECTION_STRING):
        self.connection_string = connection_string
        self.connection = None

    def connect(self):
        """Establish connection to PostgreSQL database"""
        try:
            self.connection = psycopg2.connect(self.connection_string)
            logger.info("Connected to PostgreSQL database")
            self._create_tables_if_not_exists()
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {str(e)}")
            raise

    def disconnect(self):
        """Close the database connection"""
        if self.connection:
            self.connection.close()
            logger.info("Disconnected from PostgreSQL database")

    def _create_tables_if_not_exists(self):
        """Create necessary tables if they don't exist"""
        with self.connection.cursor() as cursor:
            # Create results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS pipeline_results (
                    id SERIAL PRIMARY KEY,
                    job_id VARCHAR(255),
                    table_name VARCHAR(255),
                    pipeline_name VARCHAR(255),
                    env_id VARCHAR(255),
                    original_column VARCHAR(255),
                    fitted_column VARCHAR(255),
                    fitted_schema VARCHAR(255),
                    explanation TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create benchmark results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS benchmark_results (
                    id SERIAL PRIMARY KEY,
                    benchmark_run_id VARCHAR(255),
                    pipeline_name VARCHAR(255),
                    accuracy DECIMAL(5,4),
                    schema_accuracy DECIMAL(5,4),
                    column_accuracy DECIMAL(5,4),
                    env_accuracy DECIMAL(5,4),
                    nothing_compatible_accuracy DECIMAL(5,4),
                    total_tests INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create environment-specific benchmark results table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS env_benchmark_results (
                    id SERIAL PRIMARY KEY,
                    benchmark_run_id VARCHAR(255),
                    pipeline_name VARCHAR(255),
                    env_id VARCHAR(255),
                    accuracy DECIMAL(5,4),
                    schema_accuracy DECIMAL(5,4),
                    column_accuracy DECIMAL(5,4),
                    nothing_compatible_accuracy DECIMAL(5,4),
                    total_tests INTEGER,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            self.connection.commit()

    def save_pipeline_result(self, job_id: str, table_name: str, pipeline_name: str, env_id: str, 
                           result: MatchResultsModel):
        """Save a single pipeline result to the database"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO pipeline_results 
                    (job_id, table_name, pipeline_name, env_id, original_column, 
                    fitted_column, fitted_schema, explanation)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    job_id, table_name, pipeline_name, env_id, 
                    result.original_column, 
                    result.fitted_column, 
                    result.fitted_schema, 
                    result.explanation
                ))
                self.connection.commit()
                logger.info(f"Saved pipeline result for job {job_id}, pipeline {pipeline_name}")
        except Exception as e:
            logger.error(f"Failed to save pipeline result: {str(e)}")
            self.connection.rollback()
            raise

    def save_benchmark_results(self, benchmark_run_id: str, pipeline_name: str, 
                             metrics: Dict[str, float], total_tests: int):
        """Save benchmark results to the database"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO benchmark_results 
                    (benchmark_run_id, pipeline_name, accuracy, schema_accuracy, column_accuracy, 
                     env_accuracy, nothing_compatible_accuracy, total_tests)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    benchmark_run_id, pipeline_name,
                    metrics.get('accuracy', 0.0),
                    metrics.get('schema_accuracy', 0.0),
                    metrics.get('column_accuracy', 0.0),
                    metrics.get('env_accuracy', 0.0),
                    metrics.get('nothing_compatible_accuracy', 0.0),
                    total_tests
                ))
                self.connection.commit()
                logger.info(f"Saved benchmark results for {pipeline_name}")
        except Exception as e:
            logger.error(f"Failed to save benchmark results: {str(e)}")
            self.connection.rollback()
            raise

    def save_env_benchmark_results(self, benchmark_run_id: str, pipeline_name: str, env_id: str,
                                 metrics: Dict[str, float], total_tests: int):
        """Save environment-specific benchmark results to the database"""
        try:
            with self.connection.cursor() as cursor:
                cursor.execute("""
                    INSERT INTO env_benchmark_results 
                    (benchmark_run_id, pipeline_name, env_id, accuracy, schema_accuracy, 
                     column_accuracy, nothing_compatible_accuracy, total_tests)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    benchmark_run_id, pipeline_name, env_id,
                    metrics.get('accuracy', 0.0),
                    metrics.get('schema_accuracy', 0.0),
                    metrics.get('column_accuracy', 0.0),
                    metrics.get('nothing_compatible_accuracy', 0.0),
                    total_tests
                ))
                self.connection.commit()
                logger.info(f"Saved environment-specific benchmark results for {pipeline_name} in {env_id}")
        except Exception as e:
            logger.error(f"Failed to save environment-specific benchmark results: {str(e)}")
            self.connection.rollback()
            raise

    def get_env_benchmark_results(self, pipeline_name: str, env_id: str = None) -> List[Dict[str, Any]]:
        """Retrieve environment-specific benchmark results for a specific pipeline and optionally a specific environment"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                if env_id:
                    cursor.execute("""
                        SELECT * FROM env_benchmark_results 
                        WHERE pipeline_name = %s AND env_id = %s 
                        ORDER BY timestamp DESC
                    """, (pipeline_name, env_id))
                else:
                    cursor.execute("""
                        SELECT * FROM env_benchmark_results 
                        WHERE pipeline_name = %s ORDER BY timestamp DESC
                    """, (pipeline_name,))
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to retrieve environment-specific benchmark results for pipeline {pipeline_name}: {str(e)}")
            return []

    def get_pipeline_results(self, job_id: str) -> List[Dict[str, Any]]:
        """Retrieve pipeline results for a specific job"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM pipeline_results WHERE job_id = %s ORDER BY timestamp
                """, (job_id,))
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to retrieve pipeline results for job {job_id}: {str(e)}")
            return []

    def get_pipeline_results_by_pipeline_name(self, pipeline_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Retrieve pipeline results for a specific pipeline name"""
        try:
            # Check if connection exists and is valid, otherwise connect
            if not self.connection or self.connection.closed:
                self.connect()
            
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM pipeline_results WHERE pipeline_name = %s ORDER BY timestamp DESC LIMIT %s
                """, (pipeline_name, limit))
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to retrieve pipeline results for pipeline {pipeline_name}: {str(e)}")
            return []

    def get_benchmark_results(self, pipeline_name: str) -> List[Dict[str, Any]]:
        """Retrieve benchmark results for a specific pipeline"""
        try:
            with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
                cursor.execute("""
                    SELECT * FROM benchmark_results WHERE pipeline_name = %s ORDER BY timestamp DESC
                """, (pipeline_name,))
                results = cursor.fetchall()
                return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"Failed to retrieve benchmark results for pipeline {pipeline_name}: {str(e)}")
            return []


# Global instance for easy access
postgres_provider = PostgreSQLProvider()

