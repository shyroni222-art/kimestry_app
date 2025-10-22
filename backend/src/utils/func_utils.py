import pandas as pd
from typing import List, Dict, Any, Optional
import json
from pathlib import Path


def load_excel_file(file_path: str) -> pd.DataFrame:
    """
    Load an Excel file into a pandas DataFrame
    """
    try:
        df = pd.read_excel(file_path)
        return df
    except Exception as e:
        raise ValueError(f"Error loading Excel file {file_path}: {str(e)}")


def load_json(file_path: str) -> Any:
    """
    Load data from a JSON file
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_directory_if_not_exists(path: str) -> None:
    """
    Create a directory if it doesn't exist
    """
    Path(path).mkdir(parents=True, exist_ok=True)