# AI Question & Answering System

A modular Streamlit chat application that answers questions using Google's
Gemini API. It keeps conversation history in the current browser session so
follow-up questions can use earlier context.

## Features

- Chat-style interface with separate user and assistant messages.
- Multi-turn conversation history scoped to a Streamlit session.
- Configurable Gemini model and response temperature.
- Loading feedback, input validation, and friendly API error messages.
- API credentials loaded from a local `.env` file and never shown in the UI.
- Unit tests that mock the Gemini client and do not make network requests.

## Architecture

The Streamlit UI is in `app/main.py`. Settings are loaded and validated by
`app/config/settings.py`; `app/services/gemini_service.py` is the only module
that communicates with the Gemini API. The system prompt is maintained
separately in `app/prompts/qa_prompt.py`, and standard logging is configured in
`app/utils/logging_config.py`.

## Project structure

```text
question_answering_app/
├── app/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py
│   ├── prompts/
│   │   ├── __init__.py
│   │   └── qa_prompt.py
│   ├── services/
│   │   ├── __init__.py
│   │   └── gemini_service.py
│   ├── utils/
│   │   ├── __init__.py
│   │   └── logging_config.py
│   └── main.py
├── tests/
│   ├── __init__.py
│   ├── test_config.py
│   └── test_gemini_service.py
├── .env.example
├── .gitignore
├── README.md
├── requirements.txt
└── run.sh
```

## Prerequisites

- Python 3.10 or newer.
- A Gemini API key from [Google AI Studio](https://aistudio.google.com/apikey)
  with access to the configured model.
- `pip`.

## Setup

Run these commands from the `question_answering_app` project directory.

Create and activate a virtual environment:

```bash
python -m venv .venv
```

macOS/Linux:

```bash
source .venv/bin/activate
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Windows Command Prompt:

```bat
.venv\Scripts\activate.bat
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

Create a local environment file by copying `.env.example` to `.env`, then edit
`.env` and replace the placeholder with your own API key:

macOS/Linux:

```bash
cp .env.example .env
```

Windows PowerShell:

```powershell
Copy-Item .env.example .env
```

Configure the values in `.env`:

```dotenv
GEMINI_API_KEY=your_actual_gemini_api_key
GEMINI_MODEL=gemini-3.5-flash-lite
TEMPERATURE=0.2
```

Keep `.env` private; it is excluded by `.gitignore`. Never paste an actual key
into `.env.example`, source code, issue reports, or logs.

## Run the application

From the project directory with the virtual environment active:

```bash
streamlit run app/main.py
```

Alternatively, on macOS/Linux:

```bash
sh run.sh
```

Streamlit prints a local URL (normally `http://localhost:8501`) to open in a
browser. Enter a question in the chat box; submit another question to continue
the same session. Use **Clear Conversation** in the sidebar to reset it.

## Run tests

```bash
python -m pytest
```

The tests use mocked API responses and require neither a real API key nor
network access.

## Example questions

- What is the difference between supervised and unsupervised learning?
- Explain compound interest with a simple example.
- Summarize the main steps in the scientific method.
- Can you explain that last answer in simpler terms?

## Troubleshooting

- **Missing API key:** Create `.env` from `.env.example` and set
  `GEMINI_API_KEY`. Restart Streamlit after changing environment configuration.
- **Authentication or access error:** Confirm the key is valid and the account
  can access the model in `GEMINI_MODEL`. The UI intentionally omits provider
  error details. A quota or rate-limit error (HTTP 429) means you should check
  your Google AI Studio usage and limits for that model,
  then wait before retrying.
- **Model or parameter error:** Choose a model available to your account and
  set `TEMPERATURE` to a number from `0` to `2`. Some models may restrict
  generation parameters. The configured Gemini model must support temperature.
- **Command not found:** Activate `.venv` and install dependencies with
  `python -m pip install -r requirements.txt`.
- **Port already in use:** Start Streamlit on another port, for example
  `streamlit run app/main.py --server.port 8502`.

## Security considerations

- Store the API key only in a local `.env` file or a deployment secret manager.
- `.env` and Streamlit secrets are ignored by Git; review `git status` before
  sharing project files.
- The application does not log API keys or complete conversations. Conversation
  history is held in Streamlit session state and is not persisted by this app.
- Deployments should use HTTPS, managed secrets, access controls, rate limits,
  and an appropriate retention policy. Do not expose the app publicly without
  those controls.

## Stop the application and deactivate the environment

Press `Ctrl+C` in the terminal running Streamlit to stop the server. Deactivate
the virtual environment with:

```bash
deactivate
```

## Future enhancements

- Add configurable system prompts and per-session conversation export.
- Add authentication, request quotas, and deployment-specific secret management.
- Add streaming responses and integration tests against a controlled test API.
- Add accessibility and localization reviews.
