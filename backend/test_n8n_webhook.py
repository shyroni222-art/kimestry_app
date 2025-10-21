"""
Test script to verify the complete flow with real n8n webhook call
"""

import pandas as pd
import tempfile
import os
from src.pipeline.pipelines.n8n_pipeline import N8NPipeline
from src.providers.n8n import n8n_provider
import uuid

def test_n8n_webhook():
    print("Testing the complete flow with the n8n webhook...")
    
    # Create sample data
    sample_data = {
        "user_name": ["Alice Johnson", "Bob Smith", "Carol Davis"],
        "email_address": ["alice@example.com", "bob@example.com", "carol@example.com"],
        "user_age": [28, 35, 42],
        "location": ["Seattle", "Denver", "Miami"]
    }
    
    table_df = pd.DataFrame(sample_data)
    print(f"Sample table created with {len(table_df)} rows and {len(table_df.columns)} columns")
    print(f"Columns: {list(table_df.columns)}")
    
    # Create pipeline instance
    job_id = f"test_job_{uuid.uuid4()}"
    pipeline = N8NPipeline(name="n8n_pipeline", job_id=job_id)
    
    print(f"\nTesting direct n8n webhook call with job ID: {job_id}")
    
    # Test the n8n provider directly first
    print("\n1. Testing n8n provider with table data...")
    result = n8n_provider.send_table_data(table_df.to_dict(), "test_env", job_id)
    print(f"Direct n8n call result: {result}")
    
    # Test with pipeline
    print(f"\n2. Testing pipeline execution with job ID: {job_id}")
    try:
        results = pipeline.run("test_env", table_df)
        print(f"Pipeline returned {len(results)} results:")
        
        for i, result in enumerate(results):
            print(f"  {i+1}. {result.original_column} -> {result.fitted_column} in {result.fitted_schema}")
            print(f"     Explanation: {result.explanation}")
    
    except Exception as e:
        print(f"Pipeline execution error: {e}")
    
    print(f"\nTest completed! Job ID: {job_id}")

if __name__ == "__main__":
    test_n8n_webhook()