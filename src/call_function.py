from google.genai import types

from config import WORKING_DIRECTORY
from functions.get_files_info import get_files_info, schema_get_file_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file import write_file, schema_write_file


available_functions = types.Tool(
    function_declarations=[
        schema_get_file_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)


system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
If the user request is not clear enough, before asking for more context use the option "List files and directories" as a first step to understand the contents of the working directory.
"""


# TODO add tests
def call_function(
    function_call_part: types.FunctionCall,
    verbose=False,
) -> types.Content:
    if verbose:
        print(f" - Calling function: {function_call_part.name}({function_call_part.args})")
    else:
        print(f" - Calling function: {function_call_part.name}")

    function_name = function_call_part.name
    if function_name is None:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name="call_function",
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    function_result: str
    match function_name:
        case "get_files_info": function_result = get_files_info(WORKING_DIRECTORY, **function_call_part.args) # type: ignore
        case "get_file_content": function_result = get_file_content(WORKING_DIRECTORY, **function_call_part.args) # type: ignore
        case "run_python_file": function_result = run_python_file(WORKING_DIRECTORY, **function_call_part.args) # type: ignore
        case "write_file": function_result = write_file(WORKING_DIRECTORY, **function_call_part.args) # type: ignore
        case _:
            #return f"Error: function call for \"{function_call_part.name}\" not implemented."
            return types.Content(
                role="tool",
                parts=[
                    types.Part.from_function_response(
                        name=function_name,
                        response={"error": f"Unknown function: {function_name}"},
                    )
                ],
            )

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )


__all__ = [
    "available_functions",
    "system_prompt",
    "call_function",
]