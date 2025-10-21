from typing import List, Optional
from pydantic import BaseModel

class FieldModel(BaseModel):
    field_id: str
    field_name: str
    example_values: Optional[List[str]]
    mapping_history: Optional[List[str]]
    value_options: Optional[List[str]]
    regex: Optional[str]
    probability: str
    description: str

class SchemaModel(BaseModel):
    schema_id: str
    schema_name: str
    fields: List[FieldModel]
    description: str

class EnvModel(BaseModel):
    env_id: str
    schemas: List[SchemaModel]

class MatchResultsModel(BaseModel):
    original_column: str
    fitted_column: str
    fitted_schema: str
    explanation: str