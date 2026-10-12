import re
from pathlib import Path

from src.config import DEFAULT_DIFF_OUTPUT, DEFAULT_OUTPUT_DIR
from src.diff.version_diff import (
    load_project,
    create_diff,
    write_project
)


VERSION_PATTERN = re.compile(r"^(\d+)_(.+)$") 

def get_version_groups(input_dir):
    groups = {}

    for path in input_dir.iterdir():
        if not path.is_file():
            continue

        if path.suffix != ".jsonl":
            continue

        match = VERSION_PATTERN.match(path.name)
        if not match:
            continue

        index = int(match.group(1))
        project_name = match.group(2)

        project_number = index // 3
        version = (index % 3) + 1

        if project_number not in groups:
            groups[project_number] = {
                "name": project_name,
                "versions": {}
            }

        groups[project_number]["versions"][version] = path

    return groups



def count_functions(project):

    return sum(
        len(source_file.get("functions", []))
        for source_file in project.get("sources", [])
    )


def run_diff_pipeline(input_folder=DEFAULT_OUTPUT_DIR, diff_output=DEFAULT_DIFF_OUTPUT):
 
    input_dir = Path(input_folder)
    output_dir = Path(diff_output)

    if not input_dir.is_dir():
        print(f"Not a directory: {input_dir}")
        return 1

    output_dir.mkdir(parents=True, exist_ok=True)

    groups = get_version_groups(input_dir)

    print(f"Projects found: {len(groups)}")
    print()

    total_v1_v2 = 0
    total_v2_v3 = 0

    for project_number in sorted(groups):

        group = groups[project_number]
        versions = group["versions"]

        print(
            f"Project {project_number}: "
            f"{group['name']}"
        )

        if not all(v in versions for v in (1, 2, 3)):
            print(
                f"  Skipping diff: expected versions 1, 2, and 3, "
                f"found {sorted(versions)}"
            )
            continue

        v1_path = versions[1]
        v2_path = versions[2]
        v3_path = versions[3]

        print(f"  V1: {v1_path.name}")
        print(f"  V2: {v2_path.name}")
        print(f"  V3: {v3_path.name}")

        project_v1 = load_project(v1_path)
        project_v2 = load_project(v2_path)
        project_v3 = load_project(v3_path)

        diff_v1_v2 = create_diff(
            project_v1,
            project_v2
        )

        diff_v2_v3 = create_diff(
            project_v2,
            project_v3
        )

        added_v1_v2 = count_functions(diff_v1_v2)
        added_v2_v3 = count_functions(diff_v2_v3)

        print(
            f"  V1 -> V2: {added_v1_v2} added functions"
        )

        print(
            f"  V2 -> V3: {added_v2_v3} added functions"
        )
        project_name = project_v1["project"]["name"]
        if added_v1_v2 > 0:

           
            output_file = (
                output_dir
                / f"{project_name}_v1_v2.jsonl"
            )

            write_project(
                diff_v1_v2,
                output_file
            )

        if added_v2_v3 > 0:

            output_file = (
                output_dir
                / f"{project_name}_v2_v3.jsonl"
            )

            write_project(
                diff_v2_v3,
                output_file
            )

        total_v1_v2 += added_v1_v2
        total_v2_v3 += added_v2_v3

        print()

    print("Summary")
    print("-------")
    print(
        f"V1 -> V2 added functions: {total_v1_v2}"
    )
    print(
        f"V2 -> V3 added functions: {total_v2_v3}"
    )
    print(f"Output directory: {output_dir}")

    return 0

