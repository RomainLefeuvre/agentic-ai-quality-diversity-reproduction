from pathlib import Path

from src.utils.models import (
    ProjectEntry,
    ProjectMetadata
)

from src.normalization.serializer import JSONLSerializer

from src.parsers.python_parser import PythonParser
from src.parsers.java_parser import JavaParser
from src.utils.helper_functions import (
    detect_language,
    iter_source_files,
    load_existing_entry_ids
)


class ExtractionPipeline:

    def __init__(self, output_file):

        self.serializer = JSONLSerializer(output_file)

    def run(self, project_root: str):

        project_root = Path(project_root)
        

        language = detect_language(project_root)
        print(f"Detected language: {language}")

        existing_ids = load_existing_entry_ids(self.serializer.output_file)

        project_id = project_root.name

        # SKIP if already processed
        if project_id in existing_ids:
            print(f"Skipping {project_id} (already extracted)")
            return

        files = list(iter_source_files(project_root, language))

        print(f"Discovered {len(files)} source files")

        for f in files[:10]:
            print(f)
        parser = self._get_parser(language, project_id)

        project = ProjectEntry(
            entry_id=project_root.name,

            project=ProjectMetadata(
                name=project_root.name,
                language=language,
                repository_url=""
            )
        )

        for file_path in iter_source_files(project_root, language):

            print(f"Parsing: {file_path}")

            try:
                source_file = parser.extract(
                    file_path,
                    project_root
                )

                print(f"Functions found: {len(source_file.functions)}")

                if source_file.functions:
                    print("Appending source file")
                    project.sources.append(source_file)

            except Exception as e:
                print(f"Failed parsing {file_path}: {e}")

        print(f"Total source files stored: {len(project.sources)}")

        self.serializer.write(project)

    def _get_parser(self, language, project_id: str):
        parsers = {
            "python": PythonParser,
            "java": JavaParser,
        }

        if language not in parsers:
            raise NotImplementedError(
                f"Unsupported language '{language}' for project '{project_id}'" 
            )

        return parsers[language]()