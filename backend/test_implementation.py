import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

import pandas as pd
from src.pipeline.pipelines.n8n_pipeline import N8NPipeline
from src.utils.func_utils import create_directory_if_not_exists
from src.utils.constants import EXCEL_FILES_DIR
import uuid

def create_test_excel():
    """Create a test Excel file for testing the pipeline"""
    # Create test data
    data = {
        "Name": ["John Doe", "Jane Smith", "Bob Johnson"],
        "Email": ["john@example.com", "jane@example.com", "bob@example.com"],
        "Age": [30, 25, 40],
        "City": ["New York", "Los Angeles", "Chicago"]
    }
    
    df = pd.DataFrame(data)
    
    # Create directory if it doesn't exist
    create_directory_if_not_exists(EXCEL_FILES_DIR)
    
    # Save to Excel file
    file_path = os.path.join(EXCEL_FILES_DIR, "test_data.xlsx")
    df.to_excel(file_path, index=False)
    print(f"Test Excel file created at: {file_path}")
    
    return file_path

def test_pipeline():
    """Test the pipeline functionality"""
    print("Testing the N8N Pipeline with mock data...")
    
    # Create test Excel file
    test_file_path = create_test_excel()
    
    # Load the test file
    test_df = pd.read_excel(test_file_path)
    print(f"Loaded test data with shape: {test_df.shape}")
    print(f"Columns: {list(test_df.columns)}")
    
    # Create pipeline instance
    job_id = f"test_job_{uuid.uuid4()}"
    pipeline = N8NPipeline(name="n8n_pipeline", job_id=job_id)
    
    # Run the pipeline with mock implementation
    try:
        # Using a default environment ID
        results = pipeline.run("test_env", test_df)
        print(f"Pipeline completed with {len(results)} mock results")
        
        for i, result in enumerate(results):
            print(f"Result {i+1}: {result.original_column} -> {result.fitted_column} in {result.fitted_schema}")
            print(f"  Explanation: {result.explanation}")
        
    except Exception as e:
        print(f"Pipeline execution resulted in error: {str(e)}")
    
    print("Test completed!")

if __name__ == "__main__":
    test_pipeline()