import os

# Configuration
MICK_API_BASE_URL = os.getenv("MICK_API_BASE_URL", "http://localhost:8080/api")
POSTGRES_CONNECTION_STRING = os.getenv("POSTGRES_CONNECTION_STRING", "postgresql://user:password@localhost:5433/kimestry")
ELASTICSEARCH_URL = os.getenv("ELASTICSEARCH_URL", "http://localhost:9200")
N8N_URL = os.getenv("N8N_URL", "https://ronihabaishan.app.n8n.cloud/webhook/schema-matching")
# N8N_URL = os.getenv("N8N_URL", "https://ronihabaishan.app.n8n.cloud/webhook-test/schema-matching")

# File storage
EXCEL_FILES_DIR = os.getenv("EXCEL_FILES_DIR", "./data/excels")
GROUND_TRUTH_DIR = os.getenv("GROUND_TRUTH_DIR", "./data/ground_truth")
RESULTS_DIR = os.getenv("RESULTS_DIR", "./data/results")

# Pipeline constants
PIPELINE_TYPES = ["n8n_pipeline"]  # Only n8n pipeline as per requirements
DEFAULT_ENV_ID = "default_env"
