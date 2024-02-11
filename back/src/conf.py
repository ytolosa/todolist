import os

DATABASE_CONNECTION = os.environ.get(
    "DATABASE_CONNECTION",
    "postgresql://todolist_user:todolist_pass@localhost:5432/todolist",
)
