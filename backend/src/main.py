from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os

from src.routes.routes import router as api_router
from src.utils.logging_setup import setup_logging
from src.providers.postgress import postgres_provider
from src.utils.constants import RESULTS_DIR, EXCEL_FILES_DIR, GROUND_TRUTH_DIR, POSTGRES_CONNECTION_STRING
from src.utils.func_utils import create_directory_if_not_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan event handler for FastAPI application
    Handles startup and shutdown events
    """
    # Startup
    print("Starting Kimestry application...")
    
    # Setup logging
    setup_logging(level="DEBUG", log_file="logs/kimestry.log")
    
    # Create necessary directories
    create_directory_if_not_exists(RESULTS_DIR)
    create_directory_if_not_exists(EXCEL_FILES_DIR)
    create_directory_if_not_exists(GROUND_TRUTH_DIR)
    create_directory_if_not_exists("logs")
    
    # Connect to PostgreSQL
    try:
        print(f"Attempting to connect to PostgreSQL with connection string: {POSTGRES_CONNECTION_STRING}")
        postgres_provider.connect()
        print("Connected to PostgreSQL database successfully")
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {str(e)}")
        # We might want to handle this differently based on requirements
    
    yield  # This is where the application runs
    
    # Shutdown
    print("Shutting down Kimestry application...")
    try:
        postgres_provider.disconnect()
        print("Disconnected from PostgreSQL database")
    except Exception as e:
        print(f"Error during shutdown: {str(e)}")


# Create FastAPI application
app = FastAPI(
    title="Kimestry - Schema and Column Matching System",
    description="An LLM-powered system for matching Excel tables to database schemas and columns",
    version="1.0.0",
    lifespan=lifespan,
    debug=True  # Enable debug mode for detailed error pages
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix="/api/v1", tags=["kimestry"])

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Welcome to Kimestry - Schema and Column Matching System",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=True
    )