import argparse
from pathlib import Path

from src.config import *
from src.clone_detection.sentence_transformers_detector import (
    evaluate_sentence_transformer,
)


def main():

    parser = argparse.ArgumentParser(
        description="Run clone detection evaluation on all CSV files in a folder."
    )

    parser.add_argument(
        "--csv-folder",
        type=str, 
        default="output/",
        help="Path to folder containing function pair CSV files",
    )

    parser.add_argument(
        "--models",
        type=str,
        nargs="+",
        default=["microsoft/codebert-base-ft", "Salesforce/codet5-base-ft"],
        help="List of SentenceTransformer model names",
    )

    args = parser.parse_args()

    csv_folder = Path(args.csv_folder)

    if not csv_folder.exists():
        raise FileNotFoundError(f"Folder not found: {csv_folder}")

    csv_files = sorted(csv_folder.glob("*.csv"))

    if not csv_files:
        print(f"No CSV files found in {csv_folder}")
        return

    print(f"Found {len(csv_files)} CSV files.")

    for csv_file in csv_files:
        print(f"\nProcessing {csv_file.name}")

        for model_name in args.models:
            print(f"  Evaluating model: {model_name}")

            evaluate_sentence_transformer(
                model_name=model_name,
                csv_file=str(csv_file),
            )


if __name__ == "__main__":
    main()