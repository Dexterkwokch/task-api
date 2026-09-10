import sqlite3

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


def init_db():
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL
        )
    """)

    cursor.execute("SELECT COUNT(*) FROM tasks")
    task_count = cursor.fetchone()[0]

    if task_count == 0:
        cursor.executemany(
            "INSERT INTO tasks (title, done) VALUES (?, ?)",
            [
                ("Buy groceries", False),
                ("Study FastAPI", True),
                ("Go to the gym", False)
            ]
        )

    connection.commit()
    connection.close()


init_db()


@app.get("/", summary="Show API information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check API health")
def health():
    return {
        "status": "ok"
    }


@app.get("/tasks", summary="List all tasks")
def get_tasks():
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()

    cursor.execute("SELECT id, title, done FROM tasks")
    rows = cursor.fetchall()

    connection.close()

    tasks = []

    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "done": bool(row[2])
        })

    return tasks


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return {
        "id": row[0],
        "title": row[1],
        "done": bool(row[2])
    }


@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(request: Request):
    body = await request.json()

    title = body.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )

    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()

    cursor.execute(
        "INSERT INTO tasks (title, done) VALUES (?, ?)",
        (title.strip(), False)
    )

    connection.commit()

    new_task_id = cursor.lastrowid

    connection.close()

    return {
        "id": new_task_id,
        "title": title.strip(),
        "done": False
    }


@app.put("/tasks/{task_id}", summary="Update a task")
async def update_task(task_id: int, request: Request):
    body = await request.json()

    if not body:
        return JSONResponse(
            status_code=400,
            content={"error": "Request body cannot be empty"}
        )

    if "title" not in body and "done" not in body:
        return JSONResponse(
            status_code=400,
            content={"error": "Body must contain title and/or done"}
        )

    if "title" in body:
        title = body["title"]

        if not isinstance(title, str) or not title.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Title must be a non-empty string"}
            )

    if "done" in body:
        done = body["done"]

        if not isinstance(done, bool):
            return JSONResponse(
                status_code=400,
                content={"error": "Done must be true or false"}
            )

    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id, title, done FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    current_title = row[1]
    current_done = bool(row[2])

    new_title = body["title"].strip() if "title" in body else current_title
    new_done = body["done"] if "done" in body else current_done

    cursor.execute(
        "UPDATE tasks SET title = ?, done = ? WHERE id = ?",
        (new_title, new_done, task_id)
    )

    connection.commit()
    connection.close()

    return {
        "id": task_id,
        "title": new_title,
        "done": new_done
    }


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    connection = sqlite3.connect("tasks.db")
    cursor = connection.cursor()

    cursor.execute(
        "SELECT id FROM tasks WHERE id = ?",
        (task_id,)
    )

    row = cursor.fetchone()

    if row is None:
        connection.close()
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    cursor.execute(
        "DELETE FROM tasks WHERE id = ?",
        (task_id,)
    )

    connection.commit()
    connection.close()

    return