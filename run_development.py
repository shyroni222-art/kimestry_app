#!/usr/bin/env python3
"""
Script to run both Kimestry frontend and backend together
"""
import os
import sys
import subprocess
import threading
import time
import requests
import signal
import atexit


def check_backend_health():
    """Check if the backend is running by calling the health endpoint"""
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        return response.status_code == 200
    except:
        return False


def run_backend():
    """Run the backend server"""
    print("Starting Kimestry backend server...")
    try:
        # Start the backend server
        process = subprocess.Popen([
            sys.executable, "start_server.py"
        ], cwd=os.path.join(os.path.dirname(__file__), "backend"))
        
        # Wait a bit for the server to start
        time.sleep(3)
        
        # Check if the server started successfully
        if check_backend_health():
            print("Backend server started successfully!")
        else:
            print("Warning: Backend server may not have started properly")
        
        return process
    except Exception as e:
        print(f"Error starting backend: {e}")
        return None


def run_frontend():
    """Run the frontend development server"""
    print("Starting Kimestry frontend server...")
    try:
        # Start the frontend server
        process = subprocess.Popen([
            "npm", "start"
        ], cwd=os.path.join(os.path.dirname(__file__), "frontend"), 
        env={**os.environ, "PORT": "3000"})
        
        return process
    except Exception as e:
        print(f"Error starting frontend: {e}")
        return None


def main():
    # Change to the project root directory
    os.chdir(os.path.dirname(__file__))
    
    print("Starting Kimestry frontend and backend servers...")
    print("Backend will run on http://localhost:8000")
    print("Frontend will run on http://localhost:3000")
    print("Press Ctrl+C to stop both servers")
    
    # Start backend
    backend_process = run_backend()
    if not backend_process:
        print("Failed to start backend server. Exiting.")
        return 1
    
    # Wait a bit more for backend to fully start
    time.sleep(2)
    
    # Start frontend
    frontend_process = run_frontend()
    if not frontend_process:
        print("Failed to start frontend server. Stopping backend.")
        backend_process.terminate()
        return 1
    
    print("\nBoth servers are now running:")
    print("- Backend API: http://localhost:8000")
    print("- Frontend UI: http://localhost:3000")
    print("- API Docs: http://localhost:8000/docs")
    print("\nIf you encounter issues:")
    print("1. Check if port 8000 and 3000 are available")
    print("2. Make sure PostgreSQL is running")
    print("3. Check the console output for error messages")
    
    def signal_handler(sig, frame):
        print("\nShutting down servers...")
        if backend_process:
            backend_process.terminate()
        if frontend_process:
            frontend_process.terminate()
        sys.exit(0)
    
    # Register the signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    try:
        # Keep the script running to manage both processes
        backend_process.wait()
        frontend_process.wait()
    except KeyboardInterrupt:
        signal_handler(None, None)


if __name__ == "__main__":
    sys.exit(main())