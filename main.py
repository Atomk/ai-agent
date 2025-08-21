import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MODEL_ID
from functions.get_files_info import schema_get_file_info
from functions.get_file_content import schema_get_file_content
from functions.run_python import schema_run_python_file
from functions.write_file import schema_write_file


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    verbose = False
    if sys.argv[-1] == "--verbose":
        verbose = True
        sys.argv.pop()

    if len(sys.argv) != 2:
        print("ERROR: you need to provide the prompt as an argument")
        print("Usage: uv run main.py \"Is this a prompt?\"")
        sys.exit(1)

    prompt = sys.argv[1]
    messages = [
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
    response = client.models.generate_content(
        model=MODEL_ID,
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions],
            system_instruction=system_prompt,
        )
    )

    if response.function_calls:
        for called_function in response.function_calls:
            print(f"Calling function: {called_function.name}{called_function.args}")
    else:
        print(response.text)

    if verbose:
        print(f"User prompt: {prompt}")
        if response.usage_metadata:
            print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
            print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
            print(f"Total tokens: {response.usage_metadata.total_token_count}")
        else:
            print("ERROR: API usage data not available")

if __name__ == "__main__":
    main()
