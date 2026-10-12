import json
import pandas as pd
from pathlib import Path
from IPython.display import display, Code


def find_function_metadata(jsonl_file, function_ids):
    """Find metadata for specified function IDs in a JSONL file."""

    function_ids = set(function_ids)
    found = {}

    with open(jsonl_file, "r", encoding="utf-8") as f:

        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)

            for source in entry.get("sources", []):
                for function in source.get("functions", []):

                    function_id = function.get("function_id")

                    if function_id in function_ids:
                        found[function_id] = {
                            "function_id": function_id,
                            "name": function.get("name"),
                            "qualified_name": function.get("qualified_name"),
                            "class_name": function.get("class_name"),
                            "file_name": source.get("file_name"),
                            "relative_path": source.get("relative_path"),
                            "package": source.get("package"),
                            "start_line": function.get("start_line"),
                            "end_line": function.get("end_line"),
                        }

                    if len(found) == len(function_ids):
                        return found

    return found

def format_code(code):
    """Convert escaped newlines/tabs to actual formatting."""

    if pd.isna(code):
        return ""

    code = str(code)

    code = code.replace("\\n", "\n")
    code = code.replace("\\t", "\t")

    return code.strip()


def _get_paths(project_name):
    """Return all paths used by the qualitative-pair functions."""

    return {
        "results_json": (
            Path("../results")
            / f"{project_name}_detailed_results.json"
        ),
        "pairs_file": (
            Path("../output")
            / f"{project_name}_pairs.csv"
        ),
        "metadata_jsonl": (
            Path("../output")
            / f"{project_name}.jsonl"
        ),
    }


def _load_data(project_name):
    """Load similarity results and pair CSV."""

    paths = _get_paths(project_name)

    # Similarity results
    with open(paths["results_json"], "r", encoding="utf-8") as f:
        results = json.load(f)

    results_df = pd.DataFrame(results)

    # Make sure metrics are numeric
    results_df["sim"] = pd.to_numeric(
        results_df["sim"],
        errors="coerce",
    )

    results_df["codebleu"] = pd.to_numeric(
        results_df["codebleu"],
        errors="coerce",
    )

    # Pair CSV
    pairs_df = pd.read_csv(paths["pairs_file"])

    pairs_df["function_a_id"] = (
        pairs_df["function_a_id"]
        .astype(str)
        .str.strip()
    )

    pairs_df["function_b_id"] = (
        pairs_df["function_b_id"]
        .astype(str)
        .str.strip()
    )

    return results_df, pairs_df, paths["metadata_jsonl"]


def _display_pair(
    project_name,
    selected,
    pair,
    metadata_jsonl,
    model,
    language,
):
    """Display a selected qualitative pair."""

    pair_id = selected["pair_id"]

    function_a_id, function_b_id = pair_id.split("::")

    code_a = format_code(pair["code_a"])
    code_b = format_code(pair["code_b"])

    metadata = find_function_metadata(
        metadata_jsonl,
        [function_a_id, function_b_id],
    )

    # Overview

    print("=" * 80)
    print("QUALITATIVE EXAMPLE")
    print("=" * 80)

    print(f"Project:            {project_name}")
    print(f"Model:              {model}")
    print(f"Language:           {language}")
    print(f"Cosine similarity:  {selected['sim']:.6f}")
    print(f"CodeBLEU:           {selected['codebleu']:.6f}")

    print()
    print(f"Pair ID: {pair_id}")

    # Functions

    for label, function_id, code in [
        ("FUNCTION A", function_a_id, code_a),
        ("FUNCTION B", function_b_id, code_b),
    ]:

        info = metadata.get(function_id)

        print()
        print("=" * 80)
        print(label)
        print("=" * 80)

        if info is None:
            print("Metadata not found.")

        else:
            print(f"Function:       {info['name']}")
            print(f"Qualified name: {info['qualified_name']}")
            print(f"Class:          {info['class_name']}")
            print(f"File:           {info['file_name']}")
            print(f"Path:           {info['relative_path']}")
            print(f"Package:        {info['package']}")
            print(
                f"Lines:          "
                f"{info['start_line']}--{info['end_line']}"
            )

        print()

        display(
            Code(
                code,
                language=language,
            )
        )


def _get_pair_from_csv(
    pairs_df,
    function_a_ids,
    function_b_ids,
):
    """
    Find a pair in either orientation.

    Returns the first matching pair.
    """

    pair = pairs_df[
        (
            pairs_df["function_a_id"].isin(function_a_ids)
            &
            pairs_df["function_b_id"].isin(function_b_ids)
        )
        |
        (
            pairs_df["function_a_id"].isin(function_b_ids)
            &
            pairs_df["function_b_id"].isin(function_a_ids)
        )
    ]

    if pair.empty:
        return None

    return pair.iloc[0]


def show_qualitative_pair(
    project_name,
    sim_range=(-1.0, 1.0),
    codebleu_range=(0.0, 1.0),
    select_by="sim",
    model="microsoft/codebert-base-ft",
    language="python",
):
    """
    Find and display a qualitative pair based on
    cosine similarity and CodeBLEU ranges.

    Functions whose names contain 'test' are excluded.
    """

    if select_by not in {"sim", "codebleu"}:
        raise ValueError(
            "select_by must be either 'sim' or 'codebleu'"
        )

    results_df, pairs_df, metadata_jsonl = _load_data(
        project_name
    )

    # Exclude pairs involving functions whose names contain "test"

    test_function_ids = get_test_function_ids(
        metadata_jsonl
    )

    results_df["pair_id"] = (
        results_df["pair_id"]
        .astype(str)
        .str.strip()
    )

    pair_parts = results_df["pair_id"].str.split("::")

    results_df = results_df[
        ~pair_parts.str[0].isin(test_function_ids)
        &
        ~pair_parts.str[1].isin(test_function_ids)
    ].copy()

        # Require both functions to contain at least 4 lines of code

    pairs_df["code_lines_a"] = pairs_df["code_a"].apply(
        count_code_lines
    )

    pairs_df["code_lines_b"] = pairs_df["code_b"].apply(
        count_code_lines
    )

    valid_pairs = pairs_df[
        (pairs_df["code_lines_a"] >= 4)
        &
        (pairs_df["code_lines_b"] >= 4)
    ][
        ["function_a_id", "function_b_id"]
    ]

    valid_pair_ids = (
        valid_pairs["function_a_id"].astype(str)
        + "::"
        + valid_pairs["function_b_id"].astype(str)
    )

    valid_pair_ids_reverse = (
        valid_pairs["function_b_id"].astype(str)
        + "::"
        + valid_pairs["function_a_id"].astype(str)
    )

    results_df = results_df[
        results_df["pair_id"].isin(valid_pair_ids)
        |
        results_df["pair_id"].isin(valid_pair_ids_reverse)
    ].copy()

    # Filter by model, language, similarity, and CodeBLEU

    filtered = results_df[
        (results_df["model"] == model)
        &
        (results_df["language"] == language)
        &
        results_df["sim"].between(
            sim_range[0],
            sim_range[1],
            inclusive="both",
        )
        &
        results_df["codebleu"].between(
            codebleu_range[0],
            codebleu_range[1],
            inclusive="both",
        )
    ].copy()

    if filtered.empty:
        print("No pair satisfies the specified constraints.")
        print()
        print(f"Cosine similarity: {sim_range}")
        print(f"CodeBLEU:          {codebleu_range}")
        return

    # Select best candidate

    selected = filtered.loc[
        filtered[select_by].idxmax()
    ]

    pair_id = str(selected["pair_id"]).strip()

    try:
        function_a_id, function_b_id = pair_id.split("::")
    except ValueError:
        raise ValueError(
            f"Invalid pair_id format: {pair_id}"
        )

    # Find pair in original CSV, allowing either orientation

    pair = _get_pair_from_csv(
        pairs_df,
        {function_a_id},
        {function_b_id},
    )

    if pair is None:
        raise ValueError(
            f"Pair not found in pairs CSV:\n{pair_id}"
        )

    # Display

    _display_pair(
        project_name=project_name,
        selected=selected,
        pair=pair,
        metadata_jsonl=metadata_jsonl,
        model=model,
        language=language,
    )


def show_qualitative_pair_by_id(
    project_name,
    function_ids,
    model="microsoft/codebert-base-ft",
    language="python",
):
    """
    Find and display a specific pair using function IDs.

    The order of function_ids does not matter.
    """

    if len(function_ids) != 2:
        raise ValueError(
            "function_ids must contain exactly two IDs."
        )

    function_id_1 = str(function_ids[0]).strip()
    function_id_2 = str(function_ids[1]).strip()
    # Load data
    results_df, pairs_df, metadata_jsonl = _load_data(
        project_name
    )
    # Normalize IDs
    pairs_df["function_a_id"] = (
        pairs_df["function_a_id"]
        .astype(str)
        .str.strip()
    )

    pairs_df["function_b_id"] = (
        pairs_df["function_b_id"]
        .astype(str)
        .str.strip()
    )
    # Find pair -- BOTH orientations
    pair = pairs_df[
        (
            (pairs_df["function_a_id"] == function_id_1)
            &
            (pairs_df["function_b_id"] == function_id_2)
        )
        |
        (
            (pairs_df["function_a_id"] == function_id_2)
            &
            (pairs_df["function_b_id"] == function_id_1)
        )
    ]
    # Diagnostic information
    if pair.empty:

        print("Could not find pair.")
        print()
        print("Requested function IDs:")
        print(f"  {function_id_1}")
        print(f"  {function_id_2}")
        print()

        # Check whether each ID exists anywhere in the CSV
        id1_matches = pairs_df[
            (pairs_df["function_a_id"] == function_id_1)
            |
            (pairs_df["function_b_id"] == function_id_1)
        ]

        id2_matches = pairs_df[
            (pairs_df["function_a_id"] == function_id_2)
            |
            (pairs_df["function_b_id"] == function_id_2)
        ]

        print(
            f"Occurrences of first ID:  {len(id1_matches)}"
        )
        print(
            f"Occurrences of second ID: {len(id2_matches)}"
        )

        if not id1_matches.empty:
            print("\nPairs involving first ID:")
            print(
                id1_matches[
                    [
                        "function_a_id",
                        "function_b_id",
                    ]
                ]
                .head(10)
                .to_string(index=False)
            )

        if not id2_matches.empty:
            print("\nPairs involving second ID:")
            print(
                id2_matches[
                    [
                        "function_a_id",
                        "function_b_id",
                    ]
                ]
                .head(10)
                .to_string(index=False)
            )

        raise ValueError(
            "Pair not found in pairs CSV."
        )
    # We expect exactly one pair
    if len(pair) > 1:
        print(
            f"Warning: found {len(pair)} matching rows. "
            "Using the first."
        )

    pair = pair.iloc[0]

    actual_a_id = pair["function_a_id"]
    actual_b_id = pair["function_b_id"]
    # Find corresponding result
    # Results JSON uses pair_id = A::B
    pair_id = f"{actual_a_id}::{actual_b_id}"

    results_df["pair_id"] = (
        results_df["pair_id"]
        .astype(str)
        .str.strip()
    )

    selected = results_df[
        (results_df["pair_id"] == pair_id)
        &
        (results_df["model"] == model)
        &
        (results_df["language"] == language)
    ]

    # Try reverse orientation
    if selected.empty:

        reverse_pair_id = (
            f"{actual_b_id}::{actual_a_id}"
        )

        selected = results_df[
            (results_df["pair_id"] == reverse_pair_id)
            &
            (results_df["model"] == model)
            &
            (results_df["language"] == language)
        ]

    if selected.empty:

        raise ValueError(
            "Pair was found in CSV, but no matching "
            "similarity result was found.\n\n"
            f"CSV pair:\n"
            f"  {actual_a_id}::{actual_b_id}\n\n"
            f"Model: {model}\n"
            f"Language: {language}"
        )

    selected = selected.iloc[0]
    # Display
    _display_pair(
        project_name=project_name,
        selected=selected,
        pair=pair,
        metadata_jsonl=metadata_jsonl,
        model=model,
        language=language,
    )

def get_test_function_ids(jsonl_file):
    """Return function IDs whose name contains 'test'."""
    
    test_ids = set()

    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue

            entry = json.loads(line)

            for source in entry.get("sources", []):
                for function in source.get("functions", []):
                    function_id = function.get("function_id")
                    name = function.get("name")

                    if (
                        function_id is not None
                        and name is not None
                        and "test" in str(name).lower()
                    ):
                        test_ids.add(str(function_id).strip())

    return test_ids


def count_code_lines(code):
    """Count non-empty, non-comment lines of code."""

    code = format_code(code)

    return sum(
        1
        for line in code.splitlines()
        if line.strip()
        and not line.strip().startswith("#")
    )