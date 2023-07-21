from pydantic import BaseModel
import ast, astor


class TypeDefinitionLite(BaseModel):
    type: str
    module: str
    qualname: str

    def __eq__(self, other):
        if isinstance(other, TypeDefinitionLite):
            return self.import_path() == other.import_path()
        return False

    def import_path(self) -> str:
        return self.module + "." + self.qualname


class FunctionDeclarationLite(BaseModel):
    name: str
    qualname: str
    module_name: str
    docstring: str
    source_code: str
    signature_text: str
    imports_text: str
    query_document: str
    incomplete_file: str
    is_method: bool
    return_types: list[TypeDefinitionLite]
    params: list[TypeDefinitionLite]

    def add_pass_to_incomplete_file(self) -> None:
        self.incomplete_file += "\n    pass"

    @property
    def request_function_name(self) -> str:
        return "request_for_" + self.name

    def change_function_name_to_request_name(self) -> None:
        if not "pass" in self.incomplete_file:
            self.add_pass_to_incomplete_file()
        self.name = self.request_function_name
        module = ast.parse(self.incomplete_file)
        for statement in module.body:
            if isinstance(statement, ast.FunctionDef):
                statement.name = self.name
                break
        new_file = astor.to_source(module)
        self.incomplete_file = new_file.rstrip("\n")

    def remove_return_type_from_incomplete_file(self) -> None:
        if not "pass" in self.incomplete_file:
            self.add_pass_to_incomplete_file()
        # Parse the source code into an AST
        module = ast.parse(self.incomplete_file)

        # Find the first function definition node
        for statement in module.body:
            if isinstance(statement, ast.FunctionDef):
                # Remove the return type annotation
                statement.returns = None
                break

        # Generate the source code back from the AST
        new_source_code = astor.to_source(module)
        self.incomplete_file = new_source_code.rstrip("\n")

    def remove_import_from_incomplete_file(
        self, modulename: str, qualname: str
    ) -> None:
        if not "pass" in self.incomplete_file:
            self.add_pass_to_incomplete_file()
        module = ast.parse(self.incomplete_file)

        # Specify the object to remove and from which module
        module_to_modify = modulename
        object_to_remove = qualname

        # Remove specific import
        new_body = []
        for statement in module.body:
            if (
                isinstance(statement, ast.ImportFrom)
                and statement.module == module_to_modify
            ):
                new_names = [
                    alias for alias in statement.names if alias.name != object_to_remove
                ]
                if (
                    new_names
                ):  # if there are still objects being imported from the module
                    statement.names = new_names
                    new_body.append(statement)
            else:
                new_body.append(statement)

        module.body = new_body
        new_file = astor.to_source(module)
        self.incomplete_file = new_file.rstrip("\n")
