# Task API

A simple CRUD API built with FastAPI and SQLite.

The API allows users to create, read, update, and delete tasks.

Tasks are stored in a SQLite database, so they are not lost when the server restarts.

## Why SQLite?

SQLite is used because it is simple and does not need a separate database server.

The database is stored in a file called `tasks.db`.

If `tasks.db` does not exist, the application will create it automatically when the server starts.

## Run the Project

Create a virtual environment:

```bash
python3 -m venv .venv
```

Activate it:

```bash
source .venv/bin/activate
```

Install FastAPI and Uvicorn:

```bash
pip install fastapi uvicorn
```

Start the server:

```bash
uvicorn main:app --reload
```

The API will run at:

```text
http://127.0.0.1:8000
```

Swagger documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Database

The SQLite database is stored in:

```text
tasks.db
```

It contains a table called `tasks`.

The table has three columns:

- `id` - the task ID
- `title` - the task title
- `done` - whether the task is completed

## Database Screenshot

![SQLite Database](images/sqlite-database.png)

## Example SQL Query

This query shows all completed tasks:

```sql
SELECT * FROM tasks WHERE done = 1;
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/tasks` | Get all tasks |
| GET | `/tasks/{id}` | Get one task |
| POST | `/tasks` | Create a task |
| PUT | `/tasks/{id}` | Update a task |
| DELETE | `/tasks/{id}` | Delete a task |