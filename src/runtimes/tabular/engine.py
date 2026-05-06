import polars as pl
import duckdb
from typing import Dict, Any, Optional
import os

from .profiler import profile_dataframe
from .semantic_mapper import infer_semantic_types_with_llm
from .models import TableProfile

class TabularEngine:
    def __init__(self):
        self.conn = duckdb.connect(database=':memory:')
        self.table_profiles: Dict[str, TableProfile] = {}
        
    def register_file(self, file_path: str, table_name: str, storage_type: str = "local"):
        """
        Loads a CSV file into DuckDB and generates a semantic profile.
        storage_type can be 'local' or 's3'.
        """
        # In a real app, 's3' would download the file or use duckdb's httpfs extension.
        if storage_type == "s3":
            print(f"Mocking S3 download for {file_path}")
            # Mock: treating file_path as a local path for the MVP anyway.
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
            
        # Load into Polars for fast profiling
        df = pl.read_csv(file_path)
        
        # Profile the dataframe
        structural_profiles = profile_dataframe(df)
        
        # Map semantics using LLM mock
        semantic_models = infer_semantic_types_with_llm(list(structural_profiles.values()))
        
        # Build Table Profile
        columns_dict = {sm.column_name: sm for sm in semantic_models}
        table_profile = TableProfile(
            table_name=table_name,
            row_count=df.height,
            columns=columns_dict
        )
        self.table_profiles[table_name] = table_profile
        
        # Register the dataframe as a DuckDB table (DuckDB can query Polars DataFrames directly)
        self.conn.register(table_name, df)
        
        return table_profile
        
    def get_table_profile(self, table_name: str) -> Optional[TableProfile]:
        return self.table_profiles.get(table_name)
        
    def execute_query(self, query: str) -> pl.DataFrame:
        """
        Executes a SQL query against the loaded data and returns a Polars DataFrame.
        """
        return self.conn.execute(query).pl()
