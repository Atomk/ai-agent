import os
from google.genai import types


def write_file(
    working_directory: str,
    file_path: str,
    content: str,
) -> str:
    """Writes the provided content to a file.
    If the file already exists, it will be overwritten.
    Returns a message specifying the result of the operation.

    - working_directory: relative path from cwd to a project directory
    - file_path: relative path within the chosen working directory
    - content: the content to write to the file
    """
    # Prevent accessing anything outside of the working directory
    workdir_abspath = os.path.abspath(working_directory)
    file_abspath = os.path.abspath(os.path.join(working_directory, file_path))

    if not file_abspath.startswith(workdir_abspath):
        return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
    if os.path.exists(file_abspath) and not os.path.isfile(file_abspath):
        return f'Error: "{file_path}" exists but it\'s not a regular file'

    try:
        with open(file_abspath, "w", encoding="utf-8") as f:
            f.write(content)
        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    except Exception as exc:
        return f'Error: cannot write to file "{file_path}": {exc}'


# The `working_directory` is intentionally not listed as we won't allow the AI to specify that argument.
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description=(
        "Write the provided content to the specified file."
        " The file is constrained to the working directory."
        " If the file already exists, it will be overwritten."
    ),
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to write to, specified as a path relative to the working directory.",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The content to write to the file.",
            )
        }
    )
)
