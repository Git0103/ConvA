from src.runtimes.tabular.engine import TabularEngine
import os

def test():
    # Setup
    engine = TabularEngine()
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    csv_path = os.path.join(data_dir, "mock_survey.csv")
    
    print(f"Registering local file: {csv_path}")
    profile_local = engine.register_file(csv_path, table_name="survey_local", storage_type="local")
    print("\nLocal Profile:")
    print(profile_local.model_dump_json(indent=2))
    
    print("\nRegistering S3 mocked file:")
    profile_s3 = engine.register_file(csv_path, table_name="survey_s3", storage_type="s3")
    print("\nS3 Mocked Profile:")
    print(profile_s3.model_dump_json(indent=2))
    
    print("\nExecuting DuckDB Query (Average NPS by Region):")
    res = engine.execute_query("SELECT region, AVG(nps_score) as avg_nps FROM survey_local GROUP BY region")
    print(res)

if __name__ == "__main__":
    test()
