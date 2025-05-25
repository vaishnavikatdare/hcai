import os
import pandas as pd
from dotenv import load_dotenv


def read_dataset(file_name) -> pd.DataFrame:
    try:
        file_path = get_full_path(file_name)
        df = pd.read_csv(file_path)
        return df
    except Exception as e:
        raise RuntimeError(f"Failed to read dataset from {file_name}: {e}")


def get_full_path(file_name) -> str:
    load_dotenv()
    env_dataset_dir = os.getenv("DATASET_DIR")
    if not env_dataset_dir:
        raise ValueError("DATASET_DIR environment variable is not set.")
    return os.path.join(env_dataset_dir, file_name)
