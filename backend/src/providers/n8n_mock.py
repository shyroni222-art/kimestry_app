import requests
from typing import Dict, Any, Optional, List
from src.utils.logging_setup import get_logger
from src.utils.constants import N8N_URL

logger = get_logger(__name__)


def create_mock_response(table_df, env_schema):
    """
    Create a mock response based on the input table and schema.
    This is used when the actual n8n service is not available.
    """
    try:
        # Create mock results for each column in the DataFrame
        mock_results = []
        for col in table_df.columns:
            # Find a matching schema column based on name similarity
            matched_schema = None
            if env_schema and 'tables' in env_schema:
                for table_name, table_info in env_schema['tables'].items():
                    for column_name in table_info.get('columns', []):
                        if col.lower() in column_name.lower() or column_name.lower() in col.lower():
                            matched_schema = {
                                'table_name': table_name,
                                'column_name': column_name
                            }
                            break
                    if matched_schema:
                        break
            
            # Create mock result
            mock_result = {
                'original_column': col,
                'fitted_column': matched_schema['column_name'] if matched_schema else 'unknown_column',
                'fitted_schema': matched_schema['table_name'] if matched_schema else 'unknown_table',
                'explanation': f'Mock mapping for {col} based on schema matching logic'
            }
            mock_results.append(mock_result)
        
        logger.info(f"Created mock response with {len(mock_results)} results")
        return mock_results
    except Exception as e:
        logger.error(f"Error creating mock response: {str(e)}")
        return []


class MockN8NProvider:
    """
    Mock provider that simulates n8n behavior for testing purposes.
    This is used when the actual n8n service is not available.
    """
    
    def __init__(self, n8n_base_url: str = N8N_URL):
        self.n8n_base_url = n8n_base_url

    def send_excel_file(self, file_path: str, env_id: str, job_id: str, env_schema: dict = None) -> Optional[Dict[str, Any]]:
        """
        Mock method to send an Excel file to the n8n webhook endpoint
        """
        try:
            import pandas as pd
            # Load the Excel file to simulate processing
            df = pd.read_excel(file_path, engine='openpyxl')
            
            # Create mock response
            mock_results = create_mock_response(df, env_schema)
            
            logger.info(f"Mock n8n provider processed file for job {job_id}")
            return mock_results
        except Exception as e:
            logger.error(f"Error in mock n8n provider for job {job_id}: {str(e)}")
            return []

    def send_table_data(self, table_data: Dict[str, Any], env_id: str, job_id: str, env_schema: dict = None) -> Optional[Dict[str, Any]]:
        """
        Mock method to send table data directly to the n8n webhook endpoint as JSON
        """
        try:
            import pandas as pd
            # Convert table data to DataFrame to simulate processing
            df = pd.DataFrame(table_data)
            
            # Create mock response
            mock_results = create_mock_response(df, env_schema)
            
            logger.info(f"Mock n8n provider processed table data for job {job_id}")
            return mock_results
        except Exception as e:
            logger.error(f"Error in mock n8n provider for job {job_id}: {str(e)}")
            return []


# Optional: Global mock instance for testing
mock_n8n_provider = MockN8NProvider()