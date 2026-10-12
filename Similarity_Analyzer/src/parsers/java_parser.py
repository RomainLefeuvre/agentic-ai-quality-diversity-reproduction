from pathlib import Path


from tree_sitter import Language, Parser
import tree_sitter_java

from src.utils.models import (
    SourceFile,
    Function,
    Parameter,
    CodeBlock,
    Metrics,
    Hashes
)

from src.utils.helper_functions import (
    stable_id,
    sha256
)


class JavaParser:

    def __init__(self):

        JAVA_LANGUAGE = Language(tree_sitter_java.language())

        self.parser = Parser(JAVA_LANGUAGE)


    def extract(self, file_path: Path, project_root: Path):

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = self.parser.parse(
            bytes(source, "utf8")
        )

        relative_path = file_path.relative_to(project_root)

        source_file = SourceFile(
            source_id=stable_id(str(relative_path)),
            file_name=file_path.name,
            relative_path=str(relative_path),
            package=self._extract_package(source),
            qualified_name=self._qualified_name(relative_path)
        )

        self._extract_methods(
            tree.root_node,
            source,
            relative_path,
            source_file
        )

        return source_file


    def _extract_methods(
        self,
        node,
        source,
        relative_path,
        source_file,
        class_name=None
    ):

        if node.type == "class_declaration":

            class_name = self._child_text(
                node,
                "identifier",
                source
            )


        if node.type == "method_declaration":

            function = self._create_function(
                node,
                source,
                relative_path,
                class_name
            )

            source_file.functions.append(function)


        for child in node.children:
            self._extract_methods(
                child,
                source,
                relative_path,
                source_file,
                class_name
            )


    def _create_function(
        self,
        node,
        source,
        relative_path,
        class_name
    ):

        code = source[
            node.start_byte:
            node.end_byte
        ]

        name = self._child_text(
            node,
            "identifier",
            source
        )


        return_type = None

        type_node = node.child_by_field_name(
            "type"
        )

        if type_node:
            return_type = type_node.text.decode()


        parameters = []

        params = node.child_by_field_name(
            "parameters"
        )

        if params:

            for param in params.named_children:

                if param.type == "formal_parameter":

                    identifier = (
                        param.child_by_field_name(
                            "name"
                        )
                    )

                    if identifier:

                        parameters.append(
                            Parameter(
                                name=identifier.text.decode()
                            )
                        )


        return Function(
            function_id=stable_id(
                f"{relative_path}:{name}:{node.start_point[0]}"
            ),

            name=name,

            qualified_name=(
                f"{class_name}.{name}"
                if class_name
                else name
            ),

            class_name=class_name,

            signature=name,

            parameters=parameters,

            return_type=return_type,

            decorators=self._extract_annotations(
                node,
                source
            ),

            is_async=False,

            start_line=node.start_point[0] + 1,
            end_line=node.end_point[0] + 1,

            code=CodeBlock(
                raw=code,
                normalized=code.strip()
            ),

            metrics=Metrics(
                loc=(
                    node.end_point[0]
                    -
                    node.start_point[0]
                    + 1
                ),

                token_count=len(code.split())
            ),

            hashes=Hashes(
                raw_sha256=sha256(code),
                normalized_sha256=sha256(
                    code.strip()
                )
            )
        )


    def _extract_package(self, source):

        for line in source.splitlines():

            line = line.strip()

            if line.startswith("package "):

                return (
                    line
                    .replace("package ", "")
                    .replace(";", "")
                )

        return ""


    def _extract_annotations(
        self,
        node,
        source
    ):

        annotations = []

        for child in node.children:

            if child.type == "marker_annotation":

                annotations.append(
                    child.text.decode()
                )

        return annotations


    def _child_text(
        self,
        node,
        child_type,
        source
    ):

        for child in node.children:

            if child.type == child_type:

                return child.text.decode()

        return None


    def _qualified_name(
        self,
        relative_path
    ):

        return ".".join(
            relative_path
            .with_suffix("")
            .parts
        )