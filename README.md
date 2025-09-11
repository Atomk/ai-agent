# AI Agent

A simple AI agent to explore how this stuff works.

Uses Google's Gemini API through the `google-genai` package`.

This is a guided project part of Boot.dev's curriculum.

Code committed after [this tag](https://github.com/Atomk/ai-agent/tree/guided-project-end) is my own personal additions beyond the scope of Boot.dev's curriculum.

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
- "please fix the bug in the calculator" (after creating a simple bug like changing operator precedence)

#### Stats

Print API usage stats. Configured by default for Gemini API [free plan](https://ai.google.dev/gemini-api/docs/rate-limits#free-tier) for the [2.0 Flash](https://ai.google.dev/gemini-api/docs/pricing#gemini-2.0-flash) model.
```sh
uv run main.py stats
```

Sample output
```
Usage stats:
Tokens 24h:       5.2%    10345 / 200000
Requests 24h:     5.5%    11 / 200
Requests 60s:     0.0%    0 / 15
```

### Run tests

```sh
# Run agent functions tests
uv run tests.py
# Run stats module tests
pytest
```

### Sample project: Calculator

The agent needs some project to work on, so Boot.dev provides a "calculator" package.

```sh
uv run calculator/tests.py
# Ran 9 tests in 0.001s

$ uv run calculator/main.py "3 + 5 * 2"
# 3 + 5 = 13
```

## Extra credits

Some ideas for some features outside the scope of the guided project that I'd like to add:
- [ ] Use logging instead of printing
- [ ] Use `pytest`, plain assertions are more readable than `unittest` methods
- [x] API usage DB so you can easily see know many token/request you used (and can still use within free plan limits)
    - [x] `stats` subcommand
    - [ ] Test
    - [ ] Conversation ID
    - [ ] Save request prompt/result
- [ ] `argparse` for argument parsing
