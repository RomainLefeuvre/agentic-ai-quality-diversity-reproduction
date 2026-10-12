from src.extractor_pipeline import ExtractionPipeline 
import argparse
from pathlib import Path
from diff_pipeline import run_diff_pipeline
from diff.pairs_diff import create_pairs_from_diff
from src.utils.helper_functions import print_banner
from src.config import *


def main():

    print_banner()

    parser = argparse.ArgumentParser(
        description="Extract functions and generate function pairs."
    )

    parser.add_argument(
        "project_path",
        type=str,
        help="Path to project folder or repository collection"
    )

    parser.add_argument(
        "--output",
        type=str,
        default=DEFAULT_OUTPUT_JSONL,
        help="Output JSONL file"
    )

    parser.add_argument(
        "--pairs-output",
        type=str,
        default="output/",
        help="Output CSV containing function pairs"
    )

    parser.add_argument(
        "--entry-id",
        type=str,
        default=None,
        help="Process only a specific entry_id"
    )

    parser.add_argument(
        "--mode",
        choices=["extract", "pairs", "all"],
        default=DEFAULT_MODE,
        help="Pipeline execution mode"
    )

    args = parser.parse_args()

    path = Path(args.project_path)
    if path.is_dir() and any(p.is_dir() for p in path.iterdir()):
        _process_repositories(
            root_folder=path,
            mode=args.mode
        )
    else:

        _process_project(
            project_path=path,
            output_file=args.output,
            pairs_output=args.pairs_output,
            mode=args.mode,
            entry_id=args.entry_id
        )

def _process_project(project_path, output_file, pairs_output, mode, entry_id=None):

    print(f"\nProcessing: {project_path}")

    if mode in ("extract", "all"):
        extractor_pipeline = ExtractionPipeline(
            output_file=output_file
        )

        extractor_pipeline.run(str(project_path))
 


def _process_repositories(root_folder, mode):

    root = Path(root_folder)

    projects = [
        p for p in root.iterdir()
        if p.is_dir()
    ]

    print(f"Found {len(projects)} projects")

    for project in projects:

        project_name = project.name

        output_jsonl = (
            Path("output") /
            f"{project_name}.jsonl"
        )

        output_csv = (
            Path("output") /
            f"{project_name}_pairs.csv"
        )

        _process_project(
            project_path=project,
            output_file=str(output_jsonl),
            pairs_output=str(output_csv),
            mode=mode
        )

    if mode in ("extract", "all"):
        run_diff_pipeline()
        
    if mode in ("pairs", "all"):
        create_pairs_from_diff()

if __name__ == "__main__":
    main()