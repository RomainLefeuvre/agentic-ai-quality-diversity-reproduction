import csv
import itertools
import json
from pathlib import Path

import faiss
import torch

from src.config import *
from src.embeddings.codebert import get_model, get_tokenizer
from src.embeddings.embeddings_calc import DEFAULT_OUTPUT_DIR, build_index, embed_functions


def create_pairs_csv(jsonl_file, output_csv):
    output_file = Path(output_csv)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    with open(jsonl_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if not line:
                continue

            entry = json.loads(line)
            functions = _extract_functions_from_entry(entry)
            functions = _filter_functions(functions)

            print(
                f"{jsonl_file.name}: "
                f"{len(functions)} functions after filtering"
            )

            if len(functions) < 2:
                print("Skipping: fewer than 2 functions")
                return

            print(f"Computing embeddings for {len(functions)} functions...")

            stream = embed_functions(functions)
            index, id_map = build_index(stream)

            with open(
                output_file,
                "w",
                newline="",
                encoding="utf-8"
            ) as csvfile:

                writer = csv.writer(csvfile)

                writer.writerow([
                    "function_a_id",
                    "entry_a_id",
                    "code_a",
                    "function_b_id",
                    "entry_b_id",
                    "code_b"
                ])

                pair_count = 0

                for func_a, func_b in _generate_candidate_pairs(
                    functions,
                    index,
                    id_map,
                    k=K_NEAREST
                ):
                    writer.writerow([
                        func_a["function_id"],
                        func_a["entry_id"],
                        func_a["code"],
                        func_b["function_id"],
                        func_b["entry_id"],
                        func_b["code"]
                    ])

                    pair_count += 1

            print(f"Created: {output_file}")
            print(f"Pairs: {pair_count}")
            return


def _filter_functions(functions):
    filtered = []

    for f in functions:
        metrics = f.get("metrics", {})

        loc = metrics.get("loc", 0)
        tokens = metrics.get("token_count", 0)

        if loc < MIN_LOC:
            continue

        if tokens < MIN_TOKEN_COUNT:
            continue

        if _is_getter(f):
            continue

        if _is_setter(f):
            continue

        if is_main_function(f):
            continue

        filtered.append(f)

    return filtered


def _extract_functions_from_entry(entry):
    functions = []

    entry_id = entry["entry_id"]

    for source in entry.get("sources", []):
        for func in source.get("functions", []):
            functions.append({
                "function_id": func["function_id"],
                "entry_id": entry_id,
                "name": func.get("name"),
                "code": (
                    func["code"]["normalized"]
                    .replace("\\", "\\\\")
                    .replace("\n", "\\n")
                    .replace("\t", "\\t")
                ),
                "metrics": func.get("metrics", {})
            })

    return functions

 


def _generate_candidate_pairs(functions, index, id_map, k=K_NEAREST):
    tokenizer = get_tokenizer()
    model = get_model()

    seen = set()

    for f in functions:
        inputs = tokenizer(
            f["code"],
            return_tensors="pt",
            truncation=True,
            max_length=512
        ).to(model.device)

        with torch.inference_mode():
            outputs = model(**inputs)

        emb = (
            outputs.last_hidden_state[:, 0, :]
            .cpu()
            .numpy()
            .astype("float32")
        )

        faiss.normalize_L2(emb)

        scores, neighbors = index.search(
            emb.reshape(1, -1),
            k + 1
        )

        for j in neighbors[0][1:]:
            func_b = id_map.get(int(j))

            if func_b is None:
                continue

            a_id = f["function_id"]
            b_id = func_b["function_id"]

            pair_key = tuple(sorted((a_id, b_id)))

            if pair_key in seen:
                continue

            seen.add(pair_key)

            yield f, func_b


def _is_getter(func):
    name = func.get("name") or ""

    return (
        name.startswith(("get", "is"))
        and func.get("metrics", {}).get("loc", 0) <= 2
    )


def _is_setter(func):
    name = func.get("name") or ""

    return (
        name.startswith("set")
        and func.get("metrics", {}).get("loc", 0) <= 2
    )


def is_main_function(func):
    name = func.get("name", "")

    return name.strip().lower() in {"main", "__main__"}


def create_pairs_from_diff(input_folder=DEFAULT_DIFF_OUTPUT, pairs_output=DEFAULT_OUTPUT_DIR):
       
    input_dir = Path(input_folder)
    output_dir = Path(pairs_output)

    if not input_dir.is_dir():
        raise ValueError(f"Input directory does not exist: {input_dir}")

    output_dir.mkdir(parents=True, exist_ok=True)

    files = sorted(input_dir.glob("*.jsonl"))

    if not files:
        print(f"No diff JSONL files found in {input_dir}")
        return

    print(f"Diff files found: {len(files)}")
    print(f"Output directory: {output_dir}")
    print()

    created = 0
    skipped = 0

    for jsonl_file in files:
        output_file = output_dir / f"{jsonl_file.stem}_pairs.csv"

        print("=" * 60)
        print(f"Processing: {jsonl_file.name}")

        try:
            create_pairs_csv(
                jsonl_file,
                output_file
            )

            if output_file.exists():
                created += 1
            else:
                skipped += 1

        except Exception as e:
            skipped += 1
            print(f"Failed: {e}")

        print()

    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Diff files: {len(files)}")
    print(f"Pair files created: {created}")
    print(f"Skipped/failed: {skipped}")
    print(f"Output directory: {output_dir}")

 