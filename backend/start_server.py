#!/usr/bin/env python3
"""
Enhanced script to start the Kimestry server with better error handling and debugging capabilities
"""
import os
import sys
import uvicorn
import logging
from src.main import app
from src.providers.postgress import postgres_provider
from src.utils.logging_setup import setup_logging


def main():
    # Set up logging with maximum detail
    setup_logging(level="DEBUG", log_file="logs/kimestry.log")
    
    # Set the environment variable if not already set
    if not os.getenv('POSTGRES_CONNECTION_STRING'):
        from src.utils.constants import POSTGRES_CONNECTION_STRING
        os.environ['POSTGRES_CONNECTION_STRING'] = POSTGRES_CONNECTION_STRING
        
    # Print environment information
    print(f"Starting Kimestry server...")
    print(f"PostgreSQL connection string: {os.getenv('POSTGRES_CONNECTION_STRING', 'postgresql://user:password@localhost:5433/kimestry')}")
    print(f"Port: {int(os.getenv('PORT', 8000))}")
    print(f"Host: 0.0.0.0")
    
    # Test database connection
    try:
        postgres_provider.connect()
        print("Successfully connected to PostgreSQL database")
        postgres_provider.disconnect()
    except Exception as e:
        print(f"Could not connect to PostgreSQL database: {e}")
        print("Make sure PostgreSQL is running and the connection string is correct")
        return 1
    
    print("Server starting... Access it at:")
    print("  - Main API: http://localhost:8000")
    print("  - API Documentation: http://localhost:8000/docs") 
    print("  - Health Check: http://localhost:8000/")
    print("  - Database Status: http://localhost:8000/db/status")
    print("\nPress Ctrl+C to stop the server\n")
    
    # Start the server with uvicorn
    try:
        uvicorn.run(
            "src.main:app",
            host="0.0.0.0",
            port=int(os.getenv("PORT", 8000)),
            reload=True,
            log_level="debug",
            reload_dirs=["src/"]
        )
    except KeyboardInterrupt:
        print("\nServer stopped by user")
        return 0
    except Exception as e:
        print(f"Error starting server: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())