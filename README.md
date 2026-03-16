# MiniAgent

MiniAgent is a small command-line AI assistant built with Gemini.
It uses a simple plan → action → observe → output loop and can call local tools like:

- run shell commands
- get weather for a city
- create/read/write files
- list files in a directory

## Tech Stack

- Python
- Google Gemini (`google-generativeai`)
- `requests`, `python-dotenv`
- Langfuse `@observe` for tracing

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

```bash
pip install google-generativeai requests python-dotenv langfuse
```

3. Add your API key in `.env`:

```env
GEMINI_API_KEY=your_key_here
```

## Run

```bash
python main.py
```
