import os
import pandas as pd
from src.logger import get_logger
from src.custom__exception import CustomException
import yaml
import sys

logger = get_logger(__name__)

def read_yaml(file_path):
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        with open(file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info(f"YAML file loaded successfully: {file_path}")
            return config
        
    except Exception as e:
        logger.error(f"Error reading YAML file: {e}")
        raise CustomException("Failed to read YAML file" , e)

def load_data(file_path):
    try:
        logger.info(f"Loading data from: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        data = pd.read_csv(file_path)
        logger.info(f"Data loaded successfully from: {file_path}")
        return data

    except Exception as e:
        logger.error(f"Error loading data: {e}")
        raise CustomException("Failed to load data", e)