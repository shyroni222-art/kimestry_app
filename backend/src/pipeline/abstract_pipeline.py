from abc import ABC, abstractmethod
from typing import List
import pandas as pd

from src.utils.models import MatchResultsModel


class AbstractPipeline(ABC):
    def __init__(self, name: str, job_id: str):
        self.name = name
        self.job_id = job_id

    @abstractmethod
    def run(self, env_id: str, table_df: pd.DataFrame, env_schema: dict = None) -> List[MatchResultsModel]:
        """
        Run the pipeline on the given table data for the specified environment
        Returns a list of MatchResultsModel for each column in the table
        """
        pass