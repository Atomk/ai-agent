import os


# Prevent accidentally sending huge files to the LLM
MAX_LENGTH = 10_000


def get_file_content(working_directory: str, file_path: str) -> str:
    """Returns the contents of a file.as a string.

    If file does not exist or is not withing the chosen directory,
    returns an error as a string.

    - working_directory: relative path from cwd to a project directory
    - file_path: relative path within the chosen working directory
    """
    # Prevent accessing anything outside of the working directory
    workdir_abspath = os.path.abspath(working_directory)
    file_abspath = os.path.abspath(os.path.join(working_directory, file_path))

    if not file_abspath.startswith(workdir_abspath):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    if not os.path.isfile(file_abspath):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    try:
        with open(file_abspath, "r", encoding="utf-8") as f:
            # TODO pass MAX_LENGTH to read() as we don't need to read the whole file
            content = f.read()
            if len(content) <= MAX_LENGTH:
                return content
            else:
                return content[:MAX_LENGTH] + f'[...File "{file_path}" truncated at {MAX_LENGTH} characters]'
    except Exception as exc:
        # Allow the agent to handle unexpected errors instead of crashing
        return f"Error: cannot read file: {exc}"
