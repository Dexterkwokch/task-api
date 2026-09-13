from dotenv import load_dotenv

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.repository import PostgresTaskRepository
from app.service import TaskService

import os
import redis


load_dotenv()

app = FastAPI()

redis_client = redis.from_url(
    os.getenv("REDIS_URL"),
    decode_responses=True
)

repository = PostgresTaskRepository()
service = TaskService(repository)


@app.get("/", summary="Show API information")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


@app.get("/health", summary="Check API health")
def health():
    redis_ok = redis_client.ping()

    return {
        "status": "ok",
        "redis": redis_ok
    }


@app.get("/tasks", summary="List all tasks")
def get_tasks():
    return service.get_tasks()


@app.get("/tasks/{task_id}", summary="Get one task")
def get_task(task_id: int):
    task = service.get_task(task_id)

    if task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return task


@app.post("/tasks", status_code=201, summary="Create a new task")
async def create_task(request: Request):
    body = await request.json()

    title = body.get("title")

    if not isinstance(title, str) or not title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title is required and cannot be empty"}
        )

    return service.create_task(title.strip())


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

    current_task = service.get_task(task_id)

    if current_task is None:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
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

    new_title = (
        body["title"].strip()
        if "title" in body
        else current_task["title"]
    )

    new_done = (
        body["done"]
        if "done" in body
        else current_task["done"]
    )

    return service.update_task(
        task_id,
        new_title,
        new_done,
    )


@app.delete("/tasks/{task_id}", status_code=204, summary="Delete a task")
def delete_task(task_id: int):
    deleted = service.delete_task(task_id)

    if not deleted:
        return JSONResponse(
            status_code=404,
            content={"error": "Task not found"}
        )

    return