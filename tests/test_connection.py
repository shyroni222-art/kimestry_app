import requests

# Test the backend API
print("Testing backend connection...")

try:
    response = requests.get("http://localhost:8000/")
    if response.status_code == 200:
        print("✓ Backend is running and accessible")
        print(f"  Response: {response.json()}")
    else:
        print(f"✗ Backend returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to backend. Make sure it's running on http://localhost:8000")

print("\nTesting API endpoint...")

try:
    response = requests.get("http://localhost:8000/api/v1/benchmark")
    if response.status_code == 200:
        print("✓ API endpoint is accessible")
        data = response.json()
        print(f"  Found {len(data.get('results', {}))} pipeline results")
    else:
        print(f"✗ API endpoint returned status code: {response.status_code}")
except requests.exceptions.ConnectionError:
    print("✗ Cannot connect to API endpoint. Make sure the backend is running.")
except Exception as e:
    print(f"✗ Error accessing API: {e}")

print("\nTesting complete!")