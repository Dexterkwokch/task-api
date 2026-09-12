import os

import psycopg2


class InMemoryTaskRepository:
    def __init__(self):
        self.tasks = [
            {"id": 1, "title": "Buy groceries", "done": False},
            {"id": 2, "title": "Study FastAPI", "done": True},
            {"id": 3, "title": "Go to the gym", "done": False},
        ]
        self.next_id = 4

    def get_all(self):
        return self.tasks

    def get_by_id(self, task_id):
        for task in self.tasks:
            if task["id"] == task_id:
                return task

        return None

    def create(self, title):
        task = {
            "id": self.next_id,
            "title": title,
            "done": False,
        }

        self.tasks.append(task)
        self.next_id += 1

        return task

    def update(self, task_id, title, done):
        task = self.get_by_id(task_id)

        if task is None:
            return None

        task["title"] = title
        task["done"] = done

        return task

    def delete(self, task_id):
        task = self.get_by_id(task_id)

        if task is None:
            return False

        self.tasks.remove(task)
        return True


class PostgresTaskRepository:
    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")

    def connect(self):
        return psycopg2.connect(self.database_url)

    def get_all(self):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, title, done FROM tasks ORDER BY id"
        )

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return [
            {
                "id": row[0],
                "title": row[1],
                "done": row[2],
            }
            for row in rows
        ]

    def get_by_id(self, task_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            "SELECT id, title, done FROM tasks WHERE id = %s",
            (task_id,),
        )

        row = cursor.fetchone()

        cursor.close()
        connection.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "title": row[1],
            "done": row[2],
        }

    def create(self, title):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO tasks (title, done)
            VALUES (%s, %s)
            RETURNING id, title, done
            """,
            (title, False),
        )

        row = cursor.fetchone()

        connection.commit()

        cursor.close()
        connection.close()

        return {
            "id": row[0],
            "title": row[1],
            "done": row[2],
        }

    def update(self, task_id, title, done):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE tasks
            SET title = %s, done = %s
            WHERE id = %s
            RETURNING id, title, done
            """,
            (title, done, task_id),
        )

        row = cursor.fetchone()

        connection.commit()

        cursor.close()
        connection.close()

        if row is None:
            return None

        return {
            "id": row[0],
            "title": row[1],
            "done": row[2],
        }

    def delete(self, task_id):
        connection = self.connect()
        cursor = connection.cursor()

        cursor.execute(
            "DELETE FROM tasks WHERE id = %s RETURNING id",
            (task_id,),
        )

        row = cursor.fetchone()

        connection.commit()

        cursor.close()
        connection.close()

        return row is not None