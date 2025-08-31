# AI Agent

A simple AI agent to explore how this stuff works.

Uses Google's Gemini API through the `google-genai` package`.

This is a guided project part of Boot.dev's curriculum.

## Setup

1. Create a virtual environment and install dependencies
```sh
uv venv
source .venv/bin/activate
uv sync
```

2. Create a `.env` file in the main directory (alongside `.gitignore`) and insert your Gemini API key like this:
```ini
GEMINI_API_KEY=my_api_key_123456789
```

Other setup option are available in `config.py`.

## Usage

```sh
uv run main.py <prompt> [--verbose]
```

Try with these prompts:
- "show me what's in the root directory"
- "how does the calculator render results to the console?"
- "Please fix the bug in the calculator"

### Run tests

```sh
uv run tests.py
```

### Sample project: Calculator

The agent needs some project to work on, so Boot.dev provides a "calculator" package.

```sh
cd calculator

uv run tests.py
# Ran 9 tests in 0.001s

uv run main.py "3 + 5"
# 3 + 5 = 8
```
