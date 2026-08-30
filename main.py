from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

app = FastAPI()


tasks = [
    {"id": 1, "title": "Buy groceries", "done": False},
    {"id": 2, "title": "Study FastAPI", "done": True},
    {"id": 3, "title": "Go to the gym", "done": False}
]


@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.get("/tasks")
def get_tasks():
    return tasks


@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    for task in tasks:
        if task["id"] == task_id:
            return task

    return JSONResponse(
        status_code=404,
        content={"error": f"Task {task_id} not found"}
    )


@app.post("/tasks", status_code=201)
async def create_task(request: Request):
    body = await request.json()

    title = body.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )

    next_id = max(task["id"] for task in tasks) + 1 if tasks else 1

    new_task = {
        "id": next_id,
        "title": title.strip(),
        "done": False
    }

    tasks.append(new_task)

    return new_task