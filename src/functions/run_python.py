import os
import subprocess
from google.genai import types

from config import SUBCOMMAND_TIMEOUT_SECONDS


def run_python_file(
    working_directory: str,
    file_path: str,
    args: list | None = None
) -> str:
    """Execute a Python file located withing the provided directory.
    Command arguments can be provided as a parameter.

    WARNING: the Python file must be within the specified working directory,
    but nothing stops the executed script from accessing the rest of the filesystem.
    You've been warned.
    """
    # Prevent accessing anything outside of the working directory
    workdir_abspath = os.path.abspath(working_directory)
    file_abspath = os.path.abspath(os.path.join(working_directory, file_path))

    if not file_abspath.startswith(workdir_abspath):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    if not os.path.exists(file_abspath):
        return f'Error: File "{file_path}" not found.'
    if (not os.path.isfile(file_abspath)) or (not file_path.endswith(".py")):
        return f'Error: "{file_path}" is not a Python file.'

    script_arguments = [] if args is None else args
    command_parts = ["python3", file_abspath] + script_arguments
    try:
        completed_process = subprocess.run(
            command_parts,
            capture_output=True,
            timeout=SUBCOMMAND_TIMEOUT_SECONDS,
        )
    except Exception as exc:
        return f"Error: executing Python file: {exc}"

    lines: list[str] = []
    if completed_process.stdout:
        lines.append("STDOUT: " + str(completed_process.stdout))
    if completed_process.stderr:
        lines.append("STDERR: " + str(completed_process.stderr))
    if completed_process.returncode != 0:
        lines.append(f"Process exited with code {completed_process.returncode}")
    if len(lines) == 0:
        lines.append("No output produced.")

    return "\n".join(lines)


# The `working_directory` is intentionally not listed as we won't allow the AI to specify that argument.
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Execute the specified script file, optionally providing command.line arguments to it. The file is constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The script file to execute, specified as a path relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                    description="A single CLI argument to be passed to the script.",
                ),
                description="List of CLI arguments to pass to the script. If not provided, it means that no CLI arguments is needed. ",
            ),
        }
    )
)
