# python version_diff.py version1.jsonl version2.jsonl version_diff.jsonl
import json
import sys
from pathlib import Path


def load_project(path):
    with open(path, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) != 1:
        raise ValueError(
            f"Expected exactly one JSONL entry in {path}, "
            f"found {len(lines)}"
        )

    return json.loads(lines[0])


def function_key(function):
    return function["signature"]


def collect_signatures(project):
    return {
        function_key(function)
        for source_file in project.get("sources", [])
        for function in source_file.get("functions", [])
    }


def create_diff(project_v1, project_v2):
    signatures_v1 = collect_signatures(project_v1)
    signatures_v2 = collect_signatures(project_v2)

    added_signatures = signatures_v2 - signatures_v1

    diff_project = {
        "entry_id": project_v2["entry_id"],
        "project": project_v2["project"],
        "sources": [],
    }

    sources_by_path = {}

    for source_file in project_v2.get("sources", []):
        for function in source_file.get("functions", []):

            if function_key(function) not in added_signatures:
                continue

            path = source_file["relative_path"]

            if path not in sources_by_path:
                new_source_file = {
                    key: value
                    for key, value in source_file.items()
                    if key != "functions"
                }

                new_source_file["functions"] = []

                sources_by_path[path] = new_source_file
                diff_project["sources"].append(new_source_file)

            sources_by_path[path]["functions"].append(function)

    return diff_project


def count_functions(project):
    return sum(
        len(source_file.get("functions", []))
        for source_file in project.get("sources", [])
    )


def write_project(project, output_file):
    with open(
        output_file,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            json.dumps(
                project,
                ensure_ascii=False,
            )
        )
        f.write("\n")


def main():
    if len(sys.argv) != 4:
        print(
            "Usage: python version_diff.py "
            "<version1.jsonl> "
            "<version2.jsonl> "
            "<diff.jsonl>"
        )
        sys.exit(1)

    version1_file = Path(sys.argv[1])
    version2_file = Path(sys.argv[2])
    output_file = Path(sys.argv[3])

    print(f"Version 1: {version1_file}")
    print(f"Version 2: {version2_file}")
    print()

    project_v1 = load_project(version1_file)
    project_v2 = load_project(version2_file)

    print(f"Project: {project_v2['project']['name']}")
    print(f"Language: {project_v2['project']['language']}")

    signatures_v1 = collect_signatures(project_v1)
    signatures_v2 = collect_signatures(project_v2)

    matching = signatures_v1 & signatures_v2
    added_signatures = signatures_v2 - signatures_v1

    functions_v1 = sum(
        len(source_file.get("functions", []))
        for source_file in project_v1.get("sources", [])
    )

    functions_v2 = sum(
        len(source_file.get("functions", []))
        for source_file in project_v2.get("sources", [])
    )

    print(f"Functions in V1: {functions_v1}")
    print(f"Functions in V2: {functions_v2}")
    print(f"Unique signatures in V1: {len(signatures_v1)}")
    print(f"Unique signatures in V2: {len(signatures_v2)}")
    print(f"Matching signatures: {len(matching)}")
    print(f"Added signatures: {len(added_signatures)}")

    diff_project = create_diff(
        project_v1,
        project_v2,
    )

    added = count_functions(diff_project)

    print(f"Added functions: {added}")

    write_project(
        diff_project,
        output_file,
    )

    print()
    print(f"Output: {output_file}")


if __name__ == "__main__":
    main()
