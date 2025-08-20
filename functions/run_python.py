import os
import subprocess


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
            timeout= 30,
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
