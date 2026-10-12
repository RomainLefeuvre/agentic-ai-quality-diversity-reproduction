from pathlib import Path

import json
import pandas as pd


FILTERED_DIR = Path("output/diff")
ALL_FUNCTIONS_DIR = Path("output")
OUTPUT_FILE = Path("results/function_filtering_comparison.csv")


def get_function_ids(file):
    """Extract unique function IDs from a JSONL project file."""

    function_ids = set()

    with open(file, "r", encoding="utf-8") as f:

        for line_number, line in enumerate(f, start=1):

            line = line.strip()

            if not line:
                continue

            try:
                data = json.loads(line)
            except json.JSONDecodeError as e:
                raise RuntimeError(
                    f"Invalid JSON in {file} at line {line_number}: {e}"
                ) from e

            for source in data.get("sources", []):

                for function in source.get("functions", []):

                    function_id = function.get("function_id")

                    if function_id:
                        function_ids.add(function_id)

    return function_ids


def main():

    print("=" * 70)
    print("Comparing Functions Before and After Filtering")
    print("=" * 70)

    print(f"Filtered directory:      {FILTERED_DIR.resolve()}")
    print(f"All-functions directory: {ALL_FUNCTIONS_DIR.resolve()}")
    print(f"Output file:             {OUTPUT_FILE.resolve()}")
    print()

    filtered_files = {
        file.name: file
        for file in FILTERED_DIR.glob("*.jsonl")
        if file.is_file()
    }

    all_files = {
        file.name: file
        for file in ALL_FUNCTIONS_DIR.glob("*.jsonl")
        if file.is_file()
    }

    common_files = sorted(
        set(filtered_files) & set(all_files)
    )

    only_filtered = sorted(
        set(filtered_files) - set(all_files)
    )

    only_all = sorted(
        set(all_files) - set(filtered_files)
    )

    print(f"Filtered JSONL files:      {len(filtered_files)}")
    print(f"All-functions JSONL files: {len(all_files)}")
    print(f"Matching files:            {len(common_files)}")
    print()

    if only_filtered:
        print(
            f"WARNING: {len(only_filtered)} files exist only "
            "in the filtered directory."
        )

    if only_all:
        print(
            f"WARNING: {len(only_all)} files exist only "
            "in the all-functions directory."
        )

    print()

    rows = []

    for i, filename in enumerate(common_files, start=1):

        filtered_file = filtered_files[filename]
        all_file = all_files[filename]

        print("-" * 70)
        print(f"[{i}/{len(common_files)}] {filename}")

        print("  Reading filtered file...")
        filtered_functions = get_function_ids(
            filtered_file
        )

        print("  Reading all-functions file...")
        all_functions = get_function_ids(
            all_file
        )

        functions_before = len(all_functions)
        functions_after = len(filtered_functions)

        removed_functions = (
            all_functions - filtered_functions
        )

        functions_removed = len(removed_functions)

        if functions_before > 0:
            removed_percentage = (
                functions_removed / functions_before
            ) * 100
        else:
            removed_percentage = 0.0

        rows.append({
            "file": filename,
            "functions_before": functions_before,
            "functions_after": functions_after,
            "functions_removed": functions_removed,
            "removed_percentage": removed_percentage,
        })

        print(f"  functions before:  {functions_before}")
        print(f"  functions after:   {functions_after}")
        print(f"  functions removed: {functions_removed}")
        print(f"  removed:            {removed_percentage:.2f}%")

    if not rows:
        raise RuntimeError(
            "No matching JSONL files were found between "
            "the two directories."
        )

    df = pd.DataFrame(rows)

    OUTPUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        OUTPUT_FILE,
        index=False
    )

    print()
    print("=" * 70)
    print("SUMMARY")
    print("=" * 70)

    total_before = df["functions_before"].sum()
    total_after = df["functions_after"].sum()
    total_removed = df["functions_removed"].sum()

    if total_before > 0:
        total_removed_percentage = (
            total_removed / total_before
        ) * 100
    else:
        total_removed_percentage = 0.0

    print(f"Files compared:         {len(df)}")
    print(f"Functions before:       {total_before}")
    print(f"Functions after:        {total_after}")
    print(f"Functions removed:      {total_removed}")
    print(f"Overall removed:        {total_removed_percentage:.2f}%")

    print()
    print("Results:")
    print(df.to_string(index=False))

    print()
    print(f"Saved to: {OUTPUT_FILE.resolve()}")


if __name__ == "__main__":
    main()
