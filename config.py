MODEL_ID = "gemini-2.0-flash-001"

# Stop subcommand execution if program runs longer than the allowed time
SUBCOMMAND_TIMEOUT_SECONDS = 30

# Limits the number of characters that the agent can read from a file.
# Prevents accidentally sending huge files to the LLM.
MAX_FILE_CONTENT_LENGTH = 10_000