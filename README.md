# Focus Timer

A small desktop focus timer built with Python and PySide6.

## Features

- Track focused work for any subject or activity.
- Set an effective-time goal.
- Exclude paused time from the total.
- Automatically update the estimated end time when pausing or resuming.
- Review completed sessions grouped by date.
- Store session history locally in `records.json`.
- Save recurring daily and subject goals locally in `goals.json`.

## Requirements

- Python 3.10 or later
- Windows, Linux, or another platform supported by PySide6

## Quick start

From the project directory, run:

```powershell
python run.py
```

The launcher will:

1. Create a local `.venv` virtual environment if needed.
2. Install or update the dependencies from `requirements.txt`.
3. Start Focus Timer in an independent process.
4. Close the launcher after five seconds without closing the app.

This means you can close the terminal after starting the app. You do not need
to activate the virtual environment manually.

## Manual setup

If you prefer to manage the environment yourself:

```powershell
python -m venv .venv
```

### Windows

```powershell
.venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Linux / macOS

```bash
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Project layout

```text
focus-timer/
├── core/           # Timer and session logic
├── ui/             # PySide6 views and styling
├── main.py         # Application entry point
├── run.py          # Environment setup and launcher
└── requirements.txt
```

## Data storage

Session history is stored in `records.json` in the project directory. The file
is created or updated when sessions are recorded.
Recurring goals are stored in `goals.json` and are created when a goal is saved.
