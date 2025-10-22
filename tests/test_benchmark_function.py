import sys
import os

# Add the backend src directory to the Python path
backend_src = os.path.join(os.path.dirname(__file__), 'backend', 'src')
sys.path.insert(0, os.path.dirname(backend_src))

# Change to the backend src directory to properly import modules
original_cwd = os.getcwd()
os.chdir(backend_src)

try:
    # Import the function
    from benchmarking.pipeline_statisics import get_all_pipeline_statistics_with_wrong_matches

    print("Testing get_all_pipeline_statistics_with_wrong_matches function...")

    try:
        results = get_all_pipeline_statistics_with_wrong_matches()
        print(f"Function returned: {results}")
        print(f"Number of pipelines in results: {len(results)}")
        
        for pipeline_name, stats in results.items():
            print(f"  Pipeline: {pipeline_name}")
            print(f"    Accuracy: {stats.get('accuracy', 'N/A')}")
            print(f"    Schema Accuracy: {stats.get('schema_accuracy', 'N/A')}")
            print(f"    Total Tests: {stats.get('total_tests', 'N/A')}")
            print(f"    Wrong Matches: {len(stats.get('wrong_matches', [])) if isinstance(stats.get('wrong_matches'), list) else 'N/A'}")
            
    except Exception as e:
        print(f"Error calling function: {e}")
        import traceback
        traceback.print_exc()
        
finally:
    # Restore original working directory
    os.chdir(original_cwd)