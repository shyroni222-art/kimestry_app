"""
Combined script to run PostgreSQL and the Kimestry server for easy testing
"""
import os
import subprocess
import time
import signal
import sys
from threading import Thread
import requests
import json
from typing import List, Dict, Any

class KimestryTestRunner:
    def __init__(self):
        self.pg_process = None
        self.server_process = None
        self.is_running = False
        
    def start_postgres(self):
        """Start PostgreSQL in Docker container"""
        print("Starting PostgreSQL container...")
        try:
            # Set the environment variable first
            os.environ['POSTGRES_CONNECTION_STRING'] = 'postgresql://user:password@localhost:5433/kimestry'
            
            # Check if container is already running
            result = subprocess.run(
                ["docker", "ps", "-q", "-f", "name=kimestry-postgres"],
                capture_output=True, text=True
            )
            
            if result.stdout.strip():
                print("PostgreSQL container is already running")
            else:
                # Try to start container - create if doesn't exist
                start_result = subprocess.run(
                    ["docker", "start", "kimestry-postgres"],
                    capture_output=True, text=True
                )
                
                if start_result.returncode != 0:
                    # Container doesn't exist, create it
                    print("Creating new PostgreSQL container...")
                    create_result = subprocess.run([
                        "docker", "run", "--name", "kimestry-postgres", 
                        "-e", "POSTGRES_DB=kimestry", 
                        "-e", "POSTGRES_USER=user", 
                        "-e", "POSTGRES_PASSWORD=password", 
                        "-p", "5433:5432", "-d", "postgres:13"
                    ], capture_output=True, text=True)
                    
                    if create_result.returncode != 0:
                        print(f"Failed to create PostgreSQL container: {create_result.stderr}")
                        return False
            
            # Wait for PostgreSQL to be ready - this can take a while
            print("Waiting for PostgreSQL to be ready...")
            
            # Test the connection in a loop
            max_attempts = 30
            for attempt in range(max_attempts):
                try:
                    from src.providers.postgress import PostgreSQLProvider
                    pg_provider = PostgreSQLProvider(connection_string='postgresql://user:password@localhost:5433/kimestry')
                    pg_provider.connect()
                    pg_provider.disconnect()
                    print("PostgreSQL connection successful!")
                    return True
                except Exception as e:
                    if attempt < max_attempts - 1:  # Don't sleep on the last attempt
                        time.sleep(2)
                        print(f"Attempt {attempt + 1} failed, trying again...")
                    else:
                        print(f"Failed to connect to PostgreSQL after {max_attempts} attempts: {e}")
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error starting PostgreSQL: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def start_server(self):
        """Start the Kimestry server"""
        print("Starting Kimestry server...")
        
        # Set the environment variable for PostgreSQL
        env = os.environ.copy()
        env['POSTGRES_CONNECTION_STRING'] = 'postgresql://user:password@localhost:5433/kimestry'
        
        try:
            # Run the server in a separate process using uvicorn with more verbose output
            self.server_process = subprocess.Popen([
                sys.executable, "-m", "uvicorn", "src.main:app", 
                "--host", "0.0.0.0", "--port", "8000", "--reload", "--log-level", "debug"
            ], env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1, universal_newlines=True)
            
            # Print server output in a separate thread for debugging
            def print_output(pipe, prefix):
                for line in iter(pipe.readline, ''):
                    print(f"[{prefix}] {line.rstrip()}")
                pipe.close()
            
            from threading import Thread
            stdout_thread = Thread(target=print_output, args=(self.server_process.stdout, "STDOUT"))
            stderr_thread = Thread(target=print_output, args=(self.server_process.stderr, "STDERR"))
            stdout_thread.start()
            stderr_thread.start()
            
            # Monitor the process output to detect when the server is ready
            max_attempts = 30  # Increased attempts
            for attempt in range(max_attempts):
                # Check if the process is still running
                if self.server_process.poll() is not None:
                    print("Server process terminated unexpectedly")
                    return False
                
                # Try to connect to the server
                try:
                    response = requests.get("http://localhost:8000/", timeout=5)
                    if response.status_code == 200:
                        print("Kimestry server started successfully!")
                        # Print success message to the console
                        print(f"Server is running at: http://localhost:8000")
                        print(f"API documentation available at: http://localhost:8000/docs")
                        return True
                except requests.exceptions.RequestException:
                    pass
                time.sleep(2)  # Wait a bit longer between attempts
            
            print("Failed to start Kimestry server - timeout")
            return False
            
        except Exception as e:
            print(f"Error starting server: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def run(self):
        """Run both PostgreSQL and the server"""
        print("Starting Kimestry with PostgreSQL integration...")
        
        # Start PostgreSQL first
        if not self.start_postgres():
            print("Failed to start PostgreSQL. Exiting.")
            return False
        
        # Start the server
        if not self.start_server():
            print("Failed to start server. Attempting to stop PostgreSQL...")
            self.stop()
            return False
        
        self.is_running = True
        print("\nKimestry server is running at http://localhost:8000")
        print("API documentation available at http://localhost:8000/docs")
        print("\nPress Ctrl+C to stop both services")
        
        try:
            # Keep the script running
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\nShutting down...")
            self.stop()
        
        return True
    
    def stop(self):
        """Stop both services"""
        print("Stopping services...")
        
        if self.server_process:
            print("Terminating server process...")
            self.server_process.terminate()
            try:
                # Wait for the process to terminate, with a timeout
                self.server_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                # Force kill if it doesn't terminate gracefully
                print("Server didn't terminate gracefully, killing it...")
                self.server_process.kill()
            print("Server stopped")
        
        # Note: We don't stop the PostgreSQL container as it might be needed by other processes
        # You can stop it manually with: docker stop kimestry-postgres
        print("PostgreSQL container is still running (run 'docker stop kimestry-postgres' to stop it)")
        
        self.is_running = False


def view_saved_data():
    """
    Function to view data saved in PostgreSQL
    """
    try:
        # Set the environment variable before importing
        os.environ['POSTGRES_CONNECTION_STRING'] = 'postgresql://user:password@localhost:5433/kimestry'
        
        from src.providers.postgress import PostgreSQLProvider
        
        print("Connecting to PostgreSQL...")
        # Create a fresh instance to use the updated environment variable
        pg_provider = PostgreSQLProvider()
        pg_provider.connect()
        
        # Get all pipeline results
        with pg_provider.connection.cursor() as cursor:
            cursor.execute("""
                SELECT job_id, table_name, pipeline_name, env_id, original_column, 
                       fitted_column, fitted_schema, explanation, timestamp
                FROM pipeline_results 
                ORDER BY timestamp DESC
                LIMIT 50
            """)
            results = cursor.fetchall()
        
        if results:
            print(f"\nFound {len(results)} saved pipeline results:")
            print("-" * 120)
            print(f"{'Job ID':<15} {'Table Name':<15} {'Pipeline':<15} {'Env ID':<10} {'Orig Col':<15} {'Fitted Col':<15} {'Schema Col':<15}")
            print("-" * 120)
            
            for row in results:
                job_id, table_name, pipeline_name, env_id, orig_col, fitted_col, fitted_schema, explanation, timestamp = row
                print(f"{job_id[:14]:<15} {table_name[:14]:<15} {pipeline_name[:14]:<15} {env_id[:9]:<10} {orig_col[:14]:<15} {fitted_col[:14]:<15} {fitted_schema[:30]:<15}")
                
                if explanation:  # Print explanation on next line if it exists
                    print(f"  Explanation: {explanation[:80]}{'...' if len(explanation) > 80 else ''}")
                print()
        else:
            print("\nNo pipeline results found in database.")
        
        pg_provider.disconnect()
        return results
        
    except Exception as e:
        print(f"Error viewing saved data: {e}")
        return []


def view_benchmark_data():
    """
    Function to view benchmark data saved in PostgreSQL
    """
    try:
        # Set the environment variable before importing
        os.environ['POSTGRES_CONNECTION_STRING'] = 'postgresql://user:password@localhost:5433/kimestry'
        
        from src.providers.postgress import PostgreSQLProvider
        
        print("Connecting to PostgreSQL...")
        # Create a fresh instance to use the updated environment variable
        pg_provider = PostgreSQLProvider()
        pg_provider.connect()
        
        # Get all benchmark results
        with pg_provider.connection.cursor() as cursor:
            cursor.execute("""
                SELECT benchmark_run_id, pipeline_name, accuracy, schema_accuracy, 
                       column_accuracy, env_accuracy, nothing_compatible_accuracy, 
                       total_tests, timestamp
                FROM benchmark_results 
                ORDER BY timestamp DESC
                LIMIT 20
            """)
            results = cursor.fetchall()
        
        if results:
            print(f"\nFound {len(results)} saved benchmark results:")
            print("-" * 120)
            print(f"{'Run ID':<20} {'Pipeline':<15} {'Acc':<6} {'Schema Acc':<10} {'Col Acc':<8} {'Total Tests':<10}")
            print("-" * 120)
            
            for row in results:
                run_id, pipeline_name, accuracy, schema_acc, col_acc, env_acc, nocomp_acc, total_tests, timestamp = row
                print(f"{run_id[:19]:<20} {pipeline_name[:14]:<15} {accuracy:<6.3f} {schema_acc:<10.3f} {col_acc:<8.3f} {total_tests:<10}")
        else:
            print("\nNo benchmark results found in database.")
        
        pg_provider.disconnect()
        return results
        
    except Exception as e:
        print(f"Error viewing benchmark data: {e}")
        return []


def cleanup_useless_files():
    """
    Remove useless files from the project directory
    """
    import os
    import shutil
    from pathlib import Path
    
    print("Cleaning up useless files...")
    
    # Files and directories to remove
    useless_items = [
        "create_db.py",
        "test_end_to_end.py", 
        "test_pipeline_postgres.py",
        "test_postgres_integration.py",
        "verify_implementation.py",
        "POSTGRES_SETUP.md",
        "RUNNING_POSTGRES.md",
    ]
    
    removed_count = 0
    
    for item in useless_items:
        path = Path(item)
        if path.exists():
            if path.is_file():
                path.unlink()
                print(f"Removed file: {item}")
                removed_count += 1
            elif path.is_dir():
                shutil.rmtree(path)
                print(f"Removed directory: {item}")
                removed_count += 1
    
    print(f"\nRemoved {removed_count} useless files/directories")
    return removed_count


def clear_postgres_data():
    """
    Clear all data from PostgreSQL tables
    """
    try:
        from src.providers.postgress import PostgreSQLProvider
        
        # Create provider with direct connection string
        connection_string = 'postgresql://user:password@localhost:5433/kimestry'
        print("Connecting to PostgreSQL...")
        pg_provider = PostgreSQLProvider(connection_string=connection_string)
        pg_provider.connect()
        
        # Clear the pipeline results table
        with pg_provider.connection.cursor() as cursor:
            cursor.execute("DELETE FROM pipeline_results;")
            pipeline_deleted = cursor.rowcount
        
        # Clear the benchmark results table  
        with pg_provider.connection.cursor() as cursor:
            cursor.execute("DELETE FROM benchmark_results;")
            benchmark_deleted = cursor.rowcount
            
        pg_provider.connection.commit()
        
        print(f"Cleared {pipeline_deleted} pipeline results and {benchmark_deleted} benchmark results")
        print("PostgreSQL data cleared successfully!")
        
        pg_provider.disconnect()
        return True
        
    except Exception as e:
        print(f"Error clearing PostgreSQL data: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_benchmark_for_all_excels():
    """
    Run benchmark for all Excel files in data/excels/env_id directories
    This function calls the benchmark endpoint which will process all env directories
    """
    import os
    import requests
    from pathlib import Path
    
    # Set the environment variable
    os.environ['POSTGRES_CONNECTION_STRING'] = 'postgresql://user:password@localhost:5433/kimestry'
    
    print("Starting benchmark for all Excel files in environment directories...")
    
    # Base directory for Excel files
    excel_base_dir = Path("data/excels")
    
    if not excel_base_dir.exists():
        print(f"Excel directory {excel_base_dir} does not exist!")
        return False
    
    # Get all environment directories
    env_dirs = [d for d in excel_base_dir.iterdir() if d.is_dir()]
    
    if not env_dirs:
        print(f"No environment directories found in {excel_base_dir}")
        return False
    
    print(f"Found {len(env_dirs)} environment directories")
    for env_dir in env_dirs:
        excel_files = list(env_dir.glob("*.xlsx")) + list(env_dir.glob("*.xls"))
        print(f"  {env_dir.name}: {len(excel_files)} Excel files")
    
    print("\nCalling the benchmark endpoint (this will process all environments)...")
    
    try:
        # Call the benchmark endpoint without specifying env_id to process all environments
        response = requests.post(
            'http://localhost:8000/api/v1/benchmark',
            data={
                'pipeline_name': 'n8n_pipeline'
                # No env_id specified - the route will process all environment directories
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Benchmark result: {result}")
            return True
        else:
            print(f"Benchmark failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_full_benchmark():
    """
    Run the /benchmark route for the n8n_pipeline
    """
    import os
    import requests
    
    # Set the environment variable
    os.environ['POSTGRES_CONNECTION_STRING'] = 'postgresql://user:password@localhost:5433/kimestry'
    
    print("Running full benchmark for n8n_pipeline...")
    
    try:
        # Call the benchmark endpoint
        response = requests.post(
            'http://localhost:8000/api/v1/benchmark',
            data={
                'pipeline_name': 'n8n_pipeline',
                'env_id': 'default_env'
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Benchmark result: {result}")
            return True
        else:
            print(f"Benchmark failed with status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"Error running benchmark: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "view_data":
            view_saved_data()
        elif sys.argv[1] == "view_benchmarks":
            view_benchmark_data()
        elif sys.argv[1] == "cleanup":
            cleanup_useless_files()
        elif sys.argv[1] == "clear_pg":
            clear_postgres_data()
        elif sys.argv[1] == "run_benchmarks":
            run_benchmark_for_all_excels()
        elif sys.argv[1] == "run_full_benchmark":
            run_full_benchmark()
        elif sys.argv[1] == "run":
            runner = KimestryTestRunner()
            runner.run()
        else:
            print("Usage: python run_kimestry.py [run|view_data|view_benchmarks|cleanup|clear_pg|run_benchmarks|run_full_benchmark]")
    else:
        print("Starting Kimestry with PostgreSQL...")
        runner = KimestryTestRunner()
        runner.run()