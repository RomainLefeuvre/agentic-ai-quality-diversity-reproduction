import re


def parse_project_identity(folder_name):

    match = re.match(
        r"^\d+_(.+)_([a-f0-9]{12})$",
        folder_name
    )

    if match:
        full_name = match.group(1)
        revision = match.group(2)

        parts = full_name.split("_")

        if len(parts) >= 2 and parts[0] == parts[1]:
            project_name = parts[0]
        else:
            project_name = full_name

        return project_name, revision

    return folder_name, None