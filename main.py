import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MODEL_ID, WORKING_DIRECTORY, MAX_ITERATIONS
from functions.get_files_info import get_files_info, schema_get_file_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python import run_python_file, schema_run_python_file
from functions.write_file import write_file, schema_write_file


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


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        print("API key not found, you need to specify it in a .env file. See the README for instructions.")
        sys.exit(1)

    verbose = False
    if sys.argv[-1] == "--verbose":
        verbose = True
        sys.argv.pop()

    if len(sys.argv) != 2:
        print("ERROR: you need to provide the prompt as an argument")
        print("Usage: uv run main.py \"Is this a prompt?\"")
        sys.exit(1)

    prompt = sys.argv[1]
    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    # Gemini Client
    client = genai.Client(api_key=api_key)

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
    """

    if verbose:
        print(f"User prompt: {prompt}")

    for iteration in range(MAX_ITERATIONS):
        if iteration > 0:
            print("\n------------------------------\n")

        if verbose:
            print("Sending request.")

        response = client.models.generate_content(
            model=MODEL_ID,
            contents=messages,
            config=types.GenerateContentConfig(
                tools=[available_functions],
                system_instruction=system_prompt,
            )
        )

        if verbose:
            print("Response received.")
            if response.usage_metadata:
                print("\nSTATS:")
                print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
                print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
                print(f"Total tokens: {response.usage_metadata.total_token_count}")
            else:
                print("ERROR: API usage data not available")

        # A list of response variations, usually just one.
        if response.candidates is None:
            print("WARNING: No response candidate found.")
        else:
            for candidate in response.candidates:
                if candidate.content:
                    messages.append(candidate.content)
                    if verbose:
                        print(f"Appending a response candidate to messages list:")
                        print(f" - Role: {candidate.content.role}")
                        if candidate.content.parts:
                            for i, part in enumerate(candidate.content.parts):
                                print(f" - Part {i}")
                                if part.text:
                                    print("   - Includes text")
                                if part.function_call:
                                    print("   - Includes a function call // " + (part.function_call.name or ""))
                        print("")

        if response.function_calls:
            for called_function in response.function_calls:
                function_call_result = call_function(called_function, verbose)
                messages.append(types.Content(
                    role="user",
                    parts=function_call_result.parts,
                ))
                if verbose:
                    try:
                        print(f"-> {function_call_result.parts[0].function_response.response}") # type: ignore
                    except Exception as exc:
                        raise ValueError(f"Invalid result structure for function \"{called_function.name}\"") from exc
        else:
            # This was the final message from the AI, no further action is needed.
            if response.text:
                print(response.text)
                break

    if iteration == MAX_ITERATIONS:
        print("ERROR: agent loop was terminated due to reaching the iterations limit.")

if __name__ == "__main__":
    main()
