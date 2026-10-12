import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()


class Config:
    SONAR_URL = os.getenv("SONAR_URL")
    SONAR_TOKEN = os.getenv("SONAR_TOKEN")
    SONAR_SCANNER_PATH = os.getenv("SONAR_SCANNER_PATH") 
    PROJECTS_DIR = Path("../projects")
    OUTPUT_FILE = Path("../results/analysis_results.jsonl")

    

