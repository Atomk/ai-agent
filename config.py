MODEL_ID = "gemini-2.0-flash-001"

SUBCOMMAND_TIMEOUT_SECONDS = 30
"""Maximum allowed execution time for a function called by the agent.
Subcommand execution should be terminated if it runs longer than this amount of seconds."""

MAX_FILE_CONTENT_LENGTH = 10_000
"""Limits the number of characters that the agent can read from a file.
Prevents accidentally sending huge files to the LLM."""

WORKING_DIRECTORY = "./calculator"
"""The functions executed by the agent should be able to access
only files and subdirectories located within this directory."""

MAX_ITERATIONS = 15
"""Maximum number of times the agent can iterate over the results of its actions.
This helps preventing infinite loops and wasting tokens."""
