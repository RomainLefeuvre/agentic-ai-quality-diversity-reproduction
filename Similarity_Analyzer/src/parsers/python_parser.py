import ast
from pathlib import Path

from src.utils.models import (
    SourceFile,
    Function,
    Parameter,
    CodeBlock,
    Metrics,
    Hashes
)

from src.utils.helper_functions import stable_id, sha256


class PythonParser:

    def extract(self, file_path: Path, project_root: Path):

        source = file_path.read_text(encoding="utf-8")

        tree = ast.parse(source)

        relative_path = file_path.relative_to(project_root)

        source_file = SourceFile(
            source_id=stable_id(str(relative_path)),
            file_name=file_path.name,
            relative_path=str(relative_path),
            package=self._extract_package(relative_path),
            qualified_name=self._qualified_module_name(relative_path)
        )

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):

                function_code = ast.get_source_segment(source, node)

                function = Function(
                    function_id=stable_id(
                        f"{relative_path}:{node.name}:{node.lineno}"
                    ),

                    name=node.name,

                    qualified_name=node.name,

                    class_name=None,

                    signature=node.name,

                    parameters=[
                        Parameter(name=arg.arg)
                        for arg in node.args.args
                    ],

                    return_type=None,

                    decorators=[
                        ast.unparse(d)
                        for d in node.decorator_list
                    ],

                    is_async=False,

                    start_line=node.lineno,
                    end_line=node.end_lineno,

                    code=CodeBlock(
                        raw=function_code,
                        normalized=function_code.strip()
                    ),

                    metrics=Metrics(
                        loc=node.end_lineno - node.lineno + 1,
                        token_count=len(function_code.split())
                    ),

                    hashes=Hashes(
                        raw_sha256=sha256(function_code),
                        normalized_sha256=sha256(function_code.strip())
                    )
                )

                source_file.functions.append(function)

        return source_file

    def _extract_package(self, relative_path: Path):

        if len(relative_path.parts) <= 1:
            return ""

        return ".".join(relative_path.parts[:-1])

    def _qualified_module_name(self, relative_path: Path):

        parts = list(relative_path.with_suffix("").parts)

        return ".".join(parts)