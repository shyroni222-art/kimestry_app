from typing import List
import pandas as pd
import tempfile
import os

from src.pipeline.abstract_pipeline import AbstractPipeline
from src.utils.models import MatchResultsModel
from src.providers.n8n import n8n_provider
from src.utils.logging_setup import get_logger

logger = get_logger(__name__)


class N8NPipeline(AbstractPipeline):
    """
    This pipeline inherits from AbstractPipeline.
    In the run method, it sends the Excel file to the n8n webhook for processing.
    """
    
    def __init__(self, name: str = "n8n_pipeline", job_id: str = "", n8n_route: str = None):
        super().__init__(name, job_id)
        self.n8n_route = n8n_route
        
    def run(self, env_id: str, table_df: pd.DataFrame, env_schema: dict = None) -> List[MatchResultsModel]:
        """
        Run the n8n pipeline by sending the table data to the n8n webhook.
        This method saves the DataFrame as an Excel file and uploads it to n8n.
        """
        logger.info(f"Running n8n pipeline for environment {env_id}, job {self.job_id}")
        
        temp_file_path = None
        try:
            # Create a temporary Excel file to send to n8n
            with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as temp_file:
                temp_file_path = temp_file.name
            # Need to close the file handle before using pandas to write to it
            table_df.to_excel(temp_file_path, index=False, engine='openpyxl')
            
            logger.info(f"Sending Excel file to n8n webhook for job {self.job_id}")
            
            # Send the Excel file to the n8n webhook with the environment schema
            results = n8n_provider.send_excel_file(temp_file_path, env_id, self.job_id, env_schema, self.n8n_route)
            
            if results is not None:
                logger.info(f"n8n pipeline completed for job {self.job_id}")
                # Process the n8n response and convert to MatchResultsModel objects
                if results:  # Check if results list is not empty
                    fixed_results = [MatchResultsModel(**res) for res in results]
                    return fixed_results
                else:
                    logger.warning(f"n8n pipeline returned empty result for job {self.job_id}")
                    return []
            else:
                logger.error(f"n8n pipeline failed for job {self.job_id}")
                return []
        
        except Exception as e:
            logger.error(f"Error running n8n pipeline for job {self.job_id}: {str(e)}")
            import traceback
            traceback.print_exc()
            # Re-raise the exception to properly propagate errors
            raise
        finally:
            # Clean up the temporary file
            if temp_file_path and os.path.exists(temp_file_path):
                try:
                    os.remove(temp_file_path)
                except Exception as e:
                    # If we can't remove the file, it's not critical for functionality
                    logger.warning(f"Could not remove temporary file {temp_file_path}: {str(e)}")