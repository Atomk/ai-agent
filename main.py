import os
from dotenv import load_dotenv
from google import genai


def main():
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    # Gemini Client
    client = genai.Client(api_key=api_key)

    MODEL = "gemini-2.0-flash-001"
    prompt = "Why is Boot.dev such a great place to learn backend development? Use one paragraph maximum."
    response = client.models.generate_content(model=MODEL, contents=prompt)

    print(response.text)
    if response.usage_metadata:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
    else:
        print("ERROR: API usage data not available")

if __name__ == "__main__":
    main()
