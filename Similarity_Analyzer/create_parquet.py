from pathlib import Path

import ijson
import pandas as pd


RESULTS_DIR = Path("results")
PARQUET_FILE = RESULTS_DIR / "clone_detection_results.parquet"


def get_generation_type(prefix):
    """Determine the generation type from the file index."""

    remainder = prefix % 3

    if remainder == 0:
        return "no_llm"

    if remainder == 1:
        return "llm"

    return "agentic"


def normalize_pair_id(pair_id):
    """Normalize a pair so A::B and B::A are treated as the same pair."""

    try:
        left, right = pair_id.split("::", 1)
    except ValueError:
        return pair_id, False

    if left == right:
        return None, True

    if left > right:
        left, right = right, left

    return f"{left}::{right}", False


def main():

    print("=" * 60)
    print("Creating dataset")
    print("=" * 60)

    print(f"Results directory: {RESULTS_DIR.resolve()}")
    print(f"Parquet file:      {PARQUET_FILE.resolve()}")
    print()

    print("Creating Parquet file...")
    print()

    rows = []
    seen_pairs = set()
    self_pairs_removed = 0
    duplicate_pairs_removed = 0

    files = sorted(
        [
            f
            for f in RESULTS_DIR.glob("*_detailed_results.json")
            if f.name.split("_")[0].isdigit()
        ],
        key=lambda f: int(f.name.split("_")[0])
    )

    print(f"Found {len(files)} JSON files")
    print()

    for i, file in enumerate(files, start=1):

        print("-" * 60)

        try:
            prefix = int(file.name.split("_")[0])
        except ValueError:
            print(f"WARNING: Could not determine index from {file.name}")
            continue

        project = "_".join(
            file.stem.split("_")[1:-3]
        )

        generation_type = get_generation_type(prefix)

        print(f"[{i}/{len(files)}] {file.name}")
        print(f"  index:            {prefix}")
        print(f"  generation type:  {generation_type}")
        print(f"  project:          {project}")

        count = 0
        self_pairs = 0
        duplicate_pairs = 0

        try:

            with open(file, "rb") as f:

                for item in ijson.items(f, "item"):

                    pair_id, is_self_pair = normalize_pair_id(
                        item["pair_id"]
                    )

                    if is_self_pair:
                        self_pairs += 1
                        self_pairs_removed += 1
                        continue

                    pair_key = (
                        project,
                        generation_type,
                        item["model"],
                        item["language"],
                        pair_id
                    )

                    if pair_key in seen_pairs:
                        duplicate_pairs += 1
                        duplicate_pairs_removed += 1
                        continue

                    seen_pairs.add(pair_key)

                    rows.append({
                        "pair_id": pair_id,
                        "file": file.name,
                        "file_index": prefix,
                        "generation_type": generation_type,
                        "project": project,
                        "model": item["model"],
                        "language": item["language"],
                        "sim": item["sim"],
                        "codebleu": item["codebleu"],
                    })

                    count += 1

        except Exception as e:

            print(f"ERROR while processing {file.name}:")
            print(e)
            raise

        print(f"  rows:             {count}")
        print(f"  self-pairs:       {self_pairs}")
        print(f"  duplicates:       {duplicate_pairs}")
        print(f"  total rows:       {len(rows)}")

    print()
    print("=" * 60)
    print("Creating DataFrame")
    print("=" * 60)

    print(f"Total rows: {len(rows)}")

    df = pd.DataFrame(rows)

    print(f"Shape: {df.shape}")
    print()

    if df.empty:
        raise RuntimeError(
            "No rows were read from the JSON files. "
            "The Parquet file will not be created."
        )

    print("Data types:")
    print(df.dtypes)

    print()
    print("=" * 60)
    print("Pair filtering")
    print("=" * 60)

    print(f"Self-pairs removed:       {self_pairs_removed}")
    print(f"Duplicate pairs removed: {duplicate_pairs_removed}")

    print()
    print("=" * 60)
    print("Generation types")
    print("=" * 60)

    print(
        df["generation_type"]
        .value_counts()
        .sort_index()
    )

    print()
    print("=" * 60)
    print("Projects")
    print("=" * 60)

    print(f"Number of projects: {df['project'].nunique()}")

    print()
    print("=" * 60)
    print("Languages")
    print("=" * 60)

    print(df["language"].value_counts())

    print()
    print("=" * 60)
    print("Writing Parquet")
    print("=" * 60)

    try:

        df.to_parquet(
            PARQUET_FILE,
            index=False
        )

    except Exception as e:

        print("ERROR while writing Parquet:")
        print(e)
        raise

    print(f"Saved to: {PARQUET_FILE.resolve()}")

    print()
    print("=" * 60)
    print("FINAL DATASET")
    print("=" * 60)

    print(f"Shape: {df.shape}")
    print()

    print("Generation types:")

    print(
        df["generation_type"]
        .value_counts()
        .sort_index()
    )

    print()
    print("Projects:")
    print(f"{df['project'].nunique()}")

    print()
    print("Languages:")
    print(df["language"].value_counts())

    print()
    print("Pair filtering:")
    print(f"Self-pairs removed:       {self_pairs_removed}")
    print(f"Duplicate pairs removed: {duplicate_pairs_removed}")

    print()
    print("First rows:")
    print(df.head())

    print()
    print("=" * 60)
    print("DONE")
    print("=" * 60)


if __name__ == "__main__":
    main()