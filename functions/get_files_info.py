import os

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
