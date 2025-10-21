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


def save_json(data: Any, file_path: str) -> None:
    """
    Save data to a JSON file
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


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


def clean_column_names(columns: List[str]) -> List[str]:
    """
    Clean column names by removing special characters and making them consistent
    """
    cleaned_columns = []
    for col in columns:
        # Convert to string if not already
        col_str = str(col)
        # Remove special characters, keep alphanumeric and spaces
        cleaned = ''.join(e for e in col_str if e.isalnum() or e.isspace())
        # Replace spaces with underscores and convert to lowercase
        cleaned = cleaned.replace(' ', '_').lower()
        cleaned_columns.append(cleaned)
    return cleaned_columns


def calculate_similarity_score(str1: str, str2: str) -> float:
    """
    Calculate a simple similarity score between two strings (0-1)
    This is a basic implementation - in a real project, you might want to use
    more sophisticated algorithms like fuzzy matching
    """
    if not str1 or not str2:
        return 0.0
    
    str1, str2 = str1.lower(), str2.lower()
    if str1 == str2:
        return 1.0
    
    # Simple character-based similarity (can be replaced with more sophisticated methods)
    common_chars = sum(min(str1.count(c), str2.count(c)) for c in set(str1 + str2))
    total_chars = len(str1) + len(str2)
    
    if total_chars == 0:
        return 0.0
    
    return 2 * common_chars / total_chars


def extract_column_examples(df: pd.DataFrame, column_name: str, num_examples: int = 3) -> List[str]:
    """
    Extract example values from a dataframe column
    """
    if column_name not in df.columns:
        return []
    
    examples = df[column_name].dropna().head(num_examples).astype(str).tolist()
    return examples