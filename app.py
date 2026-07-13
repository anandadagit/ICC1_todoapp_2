from flask import Flask, request, render_template, redirect, url_for
import os
import sqlite3
import uuid
from dotenv import load_dotenv

app = Flask(__name__)

# --- Database backend selection ---------------------------------------
# Reads a local .env file (if present) into the environment. This lets you
# keep secrets like COSMOS_KEY out of your shell history / .bashrc - see
# .env.example. In production you'd typically set these as real environment
# variables (e.g. via your host/App Service config) instead of a .env file;
# load_dotenv() won't override variables that are already set that way.
load_dotenv()

# If COSMOS_ENDPOINT is set (as an environment variable), the app stores
# tasks in Azure Cosmos DB. Otherwise it falls back to the built-in
# SQLite database, so the app works out of the box with no extra setup.
COSMOS_ENDPOINT = os.environ.get('COSMOS_ENDPOINT')
COSMOS_KEY = os.environ.get('COSMOS_KEY')
COSMOS_DB = os.environ.get('COSMOS_DB', 'ICC1db')
COSMOS_CONTAINER = os.environ.get('COSMOS_CONTAINER', 'tasks')

USE_COSMOS = bool(COSMOS_ENDPOINT)

if USE_COSMOS:
    from azure.cosmos import CosmosClient, PartitionKey

    client = CosmosClient(COSMOS_ENDPOINT, COSMOS_KEY)
    database = client.create_database_if_not_exists(id=COSMOS_DB)
    container = database.create_container_if_not_exists(
        id=COSMOS_CONTAINER,
        partition_key=PartitionKey(path="/id")
    )
else:
    def init_db():
        conn = sqlite3.connect('todo.db')
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY,
                task TEXT NOT NULL,
                priority INTEGER DEFAULT 1
            )
        ''')
        conn.commit()
        conn.close()

    init_db()


# --- Data access layer --------------------------------------------------
# Both backends are normalised to the same shape - a list of dicts with
# 'id', 'task' and 'priority' keys - so the routes and templates below
# don't need to know or care which database is actually in use.

def get_all_tasks():
    if USE_COSMOS:
        tasks = list(container.read_all_items())
        tasks.sort(key=lambda t: t.get('priority', 1))
        return tasks

    conn = sqlite3.connect('todo.db')
    cur = conn.cursor()
    cur.execute('SELECT id, task, priority FROM tasks ORDER BY priority ASC')
    rows = cur.fetchall()
    conn.close()
    return [{'id': row[0], 'task': row[1], 'priority': row[2]} for row in rows]


def create_task(task, priority):
    if USE_COSMOS:
        task_doc = {
            'id': str(uuid.uuid4()),
            'task': task,
            'priority': priority
        }
        container.upsert_item(task_doc)
        return

    conn = sqlite3.connect('todo.db')
    cur = conn.cursor()
    cur.execute('INSERT INTO tasks (task, priority) VALUES (?, ?)', (task, priority))
    conn.commit()
    conn.close()


def remove_task(task_id):
    if USE_COSMOS:
        container.delete_item(item=task_id, partition_key=task_id)
        return

    conn = sqlite3.connect('todo.db')
    cur = conn.cursor()
    cur.execute('DELETE FROM tasks WHERE id = ?', (task_id,))
    conn.commit()
    conn.close()


# --- Routes ---------------------------------------------------------------

# Route for the home page
@app.route('/')
def home():
    return render_template('index.html')  # Render a home page with a link to the task manager


# Route for the task manager page
@app.route('/tasks')
def tasks():
    return render_template('tasks.html', tasks=get_all_tasks())


# Route to add a new task
@app.route('/add', methods=['POST'])
def add_task():
    new_task = request.form.get('task')
    priority = int(request.form.get('priority', 1))
    create_task(new_task, priority)
    return redirect(url_for('tasks'))


# Route to delete a task
@app.route('/delete/<task_id>', methods=['POST'])
def delete_task(task_id):
    remove_task(task_id)
    return redirect(url_for('tasks'))


if __name__ == '__main__':
    app.run(debug=False,
    host='0.0.0.0',
    port=8080
    )
