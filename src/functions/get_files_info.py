import os
from google.genai import types


def get_files_info(working_directory, directory="") -> str:
    """Returns a string representation of the contents of a directory.

    - working_directory: relative path from cwd to a project directory
    - directory: the relative path within the chosen working directory

    On failure, returns the error as a string.
    """
    # Prevent accessing anything outside of the working directory
    workdir_abspath = os.path.abspath(working_directory)
    subdir_abspath = os.path.abspath(os.path.join(working_directory, directory))

    if not subdir_abspath.startswith(workdir_abspath):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    if not os.path.isdir(subdir_abspath):
        return f'Error: "{directory}" is not a directory'

    try:
        lines = []
        for filename in os.listdir(subdir_abspath):
            if filename == "__pycache__":
                continue
            filepath = os.path.join(subdir_abspath, filename)
            size = os.path.getsize(filepath)
            is_dir = os.path.isdir(filepath)
            lines.append(f"- {filename}: file_size={size} bytes, is_dir={is_dir}")

        return "\n".join(lines)
    except Exception as exc:
        # Allow the agent to handle unexpected errors instead of crashing
        return f"Error: cannot list contents: {exc}"


# The `working_directory` is intentionally not listed as we won't allow the AI to specify that.
# The working directory will be hardcoded as a security measure.
schema_get_file_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            )
        }
    )
)
