import os
import sys
from dotenv import load_dotenv
from google import genai


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

    # Gemini Client
    client = genai.Client(api_key=api_key)

    MODEL = "gemini-2.0-flash-001"
    response = client.models.generate_content(model=MODEL, contents=prompt)

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
