import requests
import json

# Test the pipeline results and benchmark results
print("Testing pipeline vs benchmark results...")

# First, check pipeline results
print("\n1. Checking pipeline results...")
try:
    response = requests.get("http://localhost:8000/api/v1/db/pipeline_results")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ Found {data['results_count']} pipeline results in the database")
        
        if data['results_count'] > 0:
            print("  Sample result:")
            print(f"    Job ID: {data['results'][0]['job_id']}")
            print(f"    Pipeline: {data['results'][0]['pipeline_name']}")
            print(f"    Original Column: {data['results'][0]['original_column']}")
            print(f"    Fitted Column: {data['results'][0]['fitted_column']}")
            print(f"    Fitted Schema: {data['results'][0]['fitted_schema']}")
    else:
        print(f"  ✗ Pipeline results endpoint returned status code: {response.status_code}")
except Exception as e:
    print(f"  ✗ Error accessing pipeline results: {e}")

# Check specific pipeline results
print("\n2. Checking specific pipeline benchmark results...")
try:
    # Get all pipelines that have results
    response = requests.get("http://localhost:8000/api/v1/db/pipeline_results")
    if response.status_code == 200:
        data = response.json()
        if data['results_count'] > 0:
            # Get the first pipeline name to test
            pipeline_names = set([result['pipeline_name'] for result in data['results']])
            for pipeline_name in pipeline_names:
                print(f"    Testing pipeline: {pipeline_name}")
                
                # Check benchmark results for this pipeline
                benchmark_response = requests.get(f"http://localhost:8000/api/v1/benchmark/{pipeline_name}")
                if benchmark_response.status_code == 200:
                    benchmark_data = benchmark_response.json()
                    print(f"      ✓ Benchmark results found for {pipeline_name}")
                    print(f"        Accuracy: {benchmark_data['results'].get('accuracy', 'N/A')}")
                    print(f"        Schema Accuracy: {benchmark_data['results'].get('schema_accuracy', 'N/A')}")
                    print(f"        Total Tests: {benchmark_data['results'].get('total_tests', 'N/A')}")
                    print(f"        Wrong Matches: {len(benchmark_data['results'].get('wrong_matches', []))}")
                else:
                    print(f"      ✗ No benchmark results for {pipeline_name} (this is expected if ground truth doesn't exist)")
                    print("        This likely means no ground truth file exists for the input table.")
        else:
            print("    No pipeline results found in database")
    else:
        print(f"  ✗ Error getting pipeline results: {response.status_code}")
except Exception as e:
    print(f"  ✗ Error accessing benchmark results: {e}")

# Check all benchmark results
print("\n3. Checking all benchmark results...")
try:
    response = requests.get("http://localhost:8000/api/v1/benchmark")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ Found benchmarks for {len(data['results'])} pipeline(s)")
        for pipeline_name, metrics in data['results'].items():
            print(f"    {pipeline_name}:")
            print(f"      Accuracy: {metrics.get('accuracy', 'N/A')}")
            print(f"      Schema Accuracy: {metrics.get('schema_accuracy', 'N/A')}")
            print(f"      Total Tests: {metrics.get('total_tests', 'N/A')}")
    else:
        print(f"  ✗ Benchmark endpoint returned status code: {response.status_code}")
        print("    This might be because no ground truth data exists for your input tables")
except Exception as e:
    print(f"  ✗ Error accessing all benchmark results: {e}")

print("\nNote: To see benchmark results, you need to have ground truth data for your tables.")
print("Ground truth files should be in the format: {table_name}_gt.json")
print("and located in the ground truth directory (default: ./data/ground_truth)")