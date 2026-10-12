import json
from dataclasses import asdict


class JSONLSerializer:

    def __init__(self, output_file):
        self.output_file = output_file

    def write(self, project_entry):

        with open(self.output_file, "a", encoding="utf-8") as f:

            json.dump(
                asdict(project_entry),
                f,
                ensure_ascii=False
            )

            f.write("\n")