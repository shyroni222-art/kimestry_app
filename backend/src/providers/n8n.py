import requests
from typing import Dict, Any, Optional, List
from src.utils.logging_setup import get_logger
from src.utils.constants import N8N_URL

logger = get_logger(__name__)

class N8NProvider:
    """
    Provider that interfaces with n8n for workflow execution.
    This class provides an abstraction layer above n8n for querying and executing workflows.
    """
    
    def __init__(self, n8n_base_url: str = N8N_URL):
        self.n8n_base_url = n8n_base_url
        self.session = requests.Session()

    def send_excel_file(self, file_path: str, env_id: str, job_id: str, env_schema: dict = None, n8n_route: str = None, timeout: int = 600) -> Optional[Dict[str, Any]]:
        """
        Send an Excel file to the n8n webhook endpoint
        """
        try:
            # Use the provided route if given, otherwise use the default
            target_url = n8n_route if n8n_route else self.n8n_base_url
            
            with open(file_path, 'rb') as file:
                # Prepare the file for upload
                filename = file_path.split('/')[-1] if '/' in file_path else file_path.split('\\')[-1]
                files = {'file': (filename, file, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
                
                # Prepare form data
                data = {
                    'env_id': env_id,
                    'job_id': job_id
                }
                
                # If we have schema data, add it to the form as a JSON string
                if env_schema:
                    import json
                    data['env_schema'] = json.dumps(env_schema)  # Convert the schema dict to a JSON string
                
                logger.info(f"Sending file {filename} to n8n webhook at {target_url} for job {job_id} with timeout {timeout}s")
                
                # Add timeout to prevent hanging
                response = self.session.post(target_url, files=files, data=data, timeout=timeout)
                
                if response.status_code in [200, 201]:
                    response_json = response.json() if response.content else {}
                    logger.info(f"Excel file sent to n8n webhook successfully. Job ID: {job_id}")
                    
                    # Handle the response format: [{"output": [...]}] - a list containing a dict with "output" key
                    if isinstance(response_json, list) and len(response_json) > 0:
                        first_item = response_json[0]
                        if isinstance(first_item, dict) and "output" in first_item:
                            # The actual results are in the first item's "output" key
                            return first_item.get("output", [])
                    
                    # If response is directly an array of results
                    if isinstance(response_json, list):
                        return response_json
                        
                    # Fallback
                    return []
                else:
                    logger.error(f"Failed to send Excel file to n8n webhook. Status: {response.status_code}, Response: {response.text}")
                    return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout occurred while sending Excel file to n8n webhook for job {job_id}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error occurred while sending Excel file to n8n webhook for job {job_id}")
            return None
        except Exception as e:
            logger.error(f"Error sending Excel file to n8n webhook for job {job_id}: {str(e)}")
            return None

    def send_table_data(self, table_data: Dict[str, Any], env_id: str, job_id: str, env_schema: dict = None, n8n_route: str = None, timeout: int = 600) -> Optional[Dict[str, Any]]:
        """
        Send table data directly to the n8n webhook endpoint as JSON
        """
        try:
            # Use the provided route if given, otherwise use the default
            target_url = n8n_route if n8n_route else self.n8n_base_url
            
            payload = {
                'table_data': table_data,
                'env_id': env_id,
                'job_id': job_id
            }
            
            # Add env_schema to the payload if provided
            if env_schema:
                payload['env_schema'] = env_schema
            
            logger.info(f"Sending table data to n8n webhook at {target_url} for job {job_id} with timeout {timeout}s")
            
            # Add timeout to prevent hanging
            response = self.session.post(target_url, json=payload, timeout=timeout)
            
            if response.status_code in [200, 201]:
                response_json = response.json() if response.content else {}
                logger.info(f"Table data sent to n8n webhook successfully. Job ID: {job_id}")
                
                # Handle the response format: [{"output": [...]}] - a list containing a dict with "output" key
                if isinstance(response_json, list) and len(response_json) > 0:
                    first_item = response_json[0]
                    if isinstance(first_item, dict) and "output" in first_item:
                        # The actual results are in the first item's "output" key
                        return first_item.get("output", [])
                
                # If response is directly an array of results
                if isinstance(response_json, list):
                    return response_json
                    
                # Fallback
                return []
            else:
                logger.error(f"Failed to send table data to n8n webhook. Status: {response.status_code}, Response: {response.text}")
                return None
        except requests.exceptions.Timeout:
            logger.error(f"Timeout occurred while sending table data to n8n webhook for job {job_id}")
            return None
        except requests.exceptions.ConnectionError:
            logger.error(f"Connection error occurred while sending table data to n8n webhook for job {job_id}")
            return None
        except Exception as e:
            logger.error(f"Error sending table data to n8n webhook for job {job_id}: {str(e)}")
            return None


# Global instance for easy access
n8n_provider = N8NProvider()