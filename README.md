# ICC1_todoapp_2 - Azure

## Purpose

This repository is meant to be used as a basis for the ICC1 module at Ada.
This is the second task for the part of learning for the capstone project.
Learners will deploy this in a virtual machine on a Cloud Provider such as AWS, Azure, or GCP.

It builds directly on **[ICC1_todoapp](https://github.com/sierrajulietromeo/ICC1_todoapp)**, the first
task in the module, which stores tasks in a local SQLite database. This repo takes the same app and
adds the option to store tasks in a serverless **Azure Cosmos DB** instance instead - the database
aspect is separated from the compute, which is the next step for learners after getting the basic
app running.

Crucially, the app still works with no extra setup: if no Cosmos DB endpoint is configured, it falls
back to the same built-in SQLite database used in ICC1_todoapp. This keeps the app runnable at every
stage.

A simple Flask-based To-Do application that lets you manage tasks with priorities.

## Features

- Add, view, and delete tasks
- Tasks have priorities (lower number = higher priority)
- Data storage switches automatically depending on configuration:
  - If a Cosmos DB endpoint is configured, tasks are stored in **Azure Cosmos DB**
  - Otherwise, tasks are stored in the built-in **SQLite** database (`todo.db`), exactly as in ICC1_todoapp

### Prerequisites

- Python 3.9+
- [uv](https://docs.astral.sh/uv/) (recommended) or pip

### Installation

**Recommended: [uv](https://docs.astral.sh/uv/)**

uv installs as a single binary and doesn't need pip or a pre-existing virtual environment:

```sh
curl -LsSf https://astral.sh/uv/install.sh | sh
git clone <repo-url>
cd ICC1_todoapp_2
```

There's no separate install step - `uv run` (see "Running the App" below) creates the `.venv` and
installs the exact dependency versions from `uv.lock` automatically the first time you run the app.

**Fallback: pip + venv**

If you'd rather not install uv, `requirements.txt` is kept in sync as a plain pip fallback:

```sh
git clone <repo-url>
cd ICC1_todoapp_2
python3 -m venv venv
source venv/bin/activate      # on Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Choosing a database backend

By default the app uses the local SQLite database - no configuration needed, same as ICC1_todoapp.

To use Azure Cosmos DB instead, the app needs `COSMOS_ENDPOINT` and `COSMOS_KEY`. `COSMOS_ENDPOINT`
is what switches the backend: if it's set, the app talks to Cosmos DB (database `ICC1db`, container
`tasks` by default); if it's unset, the app falls back to SQLite. See the Tango Guide for creating a
Cosmos DB instance:
**[Separating the database from the compute](https://app.tango.us/app/workflow/Separating-the-database-from-the-compute---Creating-an-Azure-Cosmos-DB-Serverless-Instance-40067ef85d34476180b76ebea589c2a3)**

**Recommended: use a `.env` file.** `export`ing variables in the terminal only lasts for that shell
session (you'd have to re-run it every time you reconnect or reboot the VM), and it leaves your key
sitting in `.bash_history`. Instead:

1. Copy the template and fill in your own values:
    ```sh
    cp .env.example .env
    ```
2. Edit `.env` and paste in your Cosmos URI and primary key (from the Keys page in the Azure portal).
3. That's it - `app.py` loads `.env` automatically on startup via `python-dotenv`. `.env` is already
   listed in `.gitignore`, so it's never committed.

Optional overrides (set these in `.env` too, or leave unset for the defaults):

- `COSMOS_DB` - Cosmos database name (default `ICC1db`)
- `COSMOS_CONTAINER` - Cosmos container name (default `tasks`)

If you'd rather not use a `.env` file, `export COSMOS_ENDPOINT=...` in the shell still works exactly
as before - `.env` is just a more convenient, persistent way to set the same variables.

### Running the App

**Note:** Running on port 8080 does not require root privileges.

With uv:

```sh
uv run python3 app.py
```

With pip/venv (after activating your venv and installing `requirements.txt`):

```sh
python3 app.py
```

## Project Structure

- `app.py` - Main Flask application (SQLite by default, Azure Cosmos DB when `COSMOS_ENDPOINT` is set)
- `todo.db` - SQLite database (created automatically when Cosmos DB isn't configured)
- `.env.example` - Template for your local `.env` file (copy to `.env`, never commit the real one)
- `pyproject.toml` / `uv.lock` - Dependency definition and locked versions for `uv`
- `requirements.txt` - Plain pip fallback, kept in sync with `pyproject.toml`
- `templates/` - HTML templates

## License

MIT License
