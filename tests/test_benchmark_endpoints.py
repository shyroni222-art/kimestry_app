import requests

# Test the API endpoints directly
print("Testing API endpoints...")

# Get all pipeline results from the database
print("\n1. Getting all pipeline results from database...")
try:
    response = requests.get("http://localhost:8000/api/v1/db/pipeline_results")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ Found {data['results_count']} pipeline results")
        
        # Get unique pipeline names from the results
        pipeline_names = set()
        for result in data['results'][:10]:  # Just check first 10
            pipeline_names.add(result['pipeline_name'])
            print(f"    Sample: {result['pipeline_name']} - {result['original_column']} -> ({result['fitted_column']}, {result['fitted_schema']})")
        
        print(f"  Unique pipeline names found: {list(pipeline_names)}")
    else:
        print(f"  ✗ Database endpoint returned status: {response.status_code}")
        print(f"  Response: {response.text}")
except Exception as e:
    print(f"  ✗ Error: {e}")

# Test getting benchmark for a specific pipeline (if any exist)
if pipeline_names:
    for pipeline_name in list(pipeline_names)[:1]:  # Test just the first one
        print(f"\n2. Getting benchmark for pipeline: {pipeline_name}")
        try:
            response = requests.get(f"http://localhost:8000/api/v1/benchmark/{pipeline_name}")
            if response.status_code == 200:
                data = response.json()
                print(f"  ✓ Got benchmark results for {pipeline_name}")
                print(f"    Accuracy: {data['results'].get('accuracy', 'N/A')}")
                print(f"    Schema Accuracy: {data['results'].get('schema_accuracy', 'N/A')}")
                print(f"    Total Tests: {data['results'].get('total_tests', 'N/A')}")
            elif response.status_code == 404:
                print(f"  ? No benchmark results for {pipeline_name} - likely no ground truth data")
            else:
                print(f"  ✗ Benchmark endpoint returned status: {response.status_code}")
                print(f"  Response: {response.text}")
        except Exception as e:
            print(f"  ✗ Error: {e}")

# Test getting all benchmarks
print(f"\n3. Getting all benchmarks...")
try:
    response = requests.get("http://localhost:8000/api/v1/benchmark")
    if response.status_code == 200:
        data = response.json()
        print(f"  ✓ Got all benchmark results")
        print(f"  Number of pipelines with benchmarks: {len(data['results'])}")
        for pipeline_name, results in data['results'].items():
            print(f"    {pipeline_name}:")
            print(f"      Accuracy: {results.get('accuracy', 'N/A')}")
            print(f"      Schema Accuracy: {results.get('schema_accuracy', 'N/A')}")
            print(f"      Total Tests: {results.get('total_tests', 'N/A')}")
    else:
        print(f"  ✗ All benchmark endpoint returned status: {response.status_code}")
        print(f"  Response: {response.text}")
        print("  This could indicate an internal server error")
except Exception as e:
    print(f"  ✗ Error: {e}")

print("\nNote: If you don't see results in the benchmark endpoints but do see them in the raw")
print("pipeline results, it's likely because there's no ground truth available to calculate")
print("accuracy metrics. Ground truth files must exist for your input tables.")