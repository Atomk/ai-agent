import os
import sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

from config import MODEL_ID, MAX_ITERATIONS
from call_function import (
    call_function,
    available_functions,
    system_prompt,
)


def main():
    # Load API key
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    if api_key is None:
        print("API key not found, you need to specify it in a .env file. See the README for instructions.")
        sys.exit(1)

    # Parse CLI arguments
    verbose = False
    if sys.argv[-1] == "--verbose":
        verbose = True
        sys.argv.pop()

    if len(sys.argv) != 2:
        print("ERROR: you need to provide the prompt as an argument")
        print("Usage: uv run main.py \"Is this a prompt?\" [--verbose]")
        sys.exit(1)

    prompt = sys.argv[1]
    messages: list[types.Content] = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    client = genai.Client(api_key=api_key)

    if verbose:
        print(f"User prompt: {prompt}")

    for iteration in range(MAX_ITERATIONS):
        if verbose:
            if iteration > 0:
                print("\n------------------------------\n")
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
