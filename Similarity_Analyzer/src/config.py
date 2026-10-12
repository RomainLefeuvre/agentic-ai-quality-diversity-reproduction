import torch
 
DEFAULT_OUTPUT_DIR = "output/" 
DEFAULT_OUTPUT_JSONL = f"{DEFAULT_OUTPUT_DIR}projects.jsonl"
DEFAULT_DIFF_OUTPUT = f"{DEFAULT_OUTPUT_DIR}/diff/"
RESULTS_DIR = "results/"

DEFAULT_MODE = "all"
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
MODELS_PATH = "models/"


# Function filtering thresholds (pair generation stage)
MIN_LOC = 2
MIN_TOKEN_COUNT = 5
K_NEAREST = 20
TOKENIZER_NAME = "microsoft/codebert-base"