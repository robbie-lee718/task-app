import argparse
from sqlite import Sqlite
from typing import Optional

def init_db(db_path: str, table_name: str):
    """Ensure the table exists before running operations."""
    schema = {
        "name": "TEXT NOT NULL",
        "description": "TEXT"
    }
    with Sqlite(db_path, table_name) as db:
        db.create_table(schema)

def add_task(name: str, description: str, db_path: str, table_name: str):
    with Sqlite(db_path, table_name) as db:
        task_id = db.insert({"name": name, "description": description})
        print(f"Task created: {task_id}")

def update_task(task_id: int, name: Optional[str], description: Optional[str], db_path: str, table_name:str):
    with Sqlite(db_path, table_name) as db:
        tasks = db.get_all()

        if task_id < 1 or task_id > len(tasks):
            print(f"Error: Invalid task number '{task_id}'. Choose between 1 and {len(tasks)}.")
            return

        target_task = tasks[task_id - 1]
        real_db_id = target_task["id"]

        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description

        if not update_data:
            print("No changes specified. Use -n/--name or -d/--description to update.")
            return

        db.update(real_db_id, update_data)
        print(f"Updated task with ID: {task_id}")

def list_tasks(db_path: str, table_name: str):
    with Sqlite(db_path, table_name) as db:
        tasks = db.get_all()
        if not tasks:
            print("No tasks found.")
            return
        
        for display_num, task in enumerate(tasks, start=1):
            print(f"{display_num}. {task['name']} - {task['description']}")

def delete_task(task_id: int, db_path: str, table_name:str):
    with Sqlite(db_path, table_name) as db:
        tasks = db.get_all()

        if task_id < 1 or task_id > len(tasks):
            print(f"Error: Invalid task number '{task_id}'. Choose between 1 and {len(tasks)}.")
            return

        target_task = tasks[task_id - 1]
        real_db_id = target_task["id"]

        # Delete using the true database ID
        db.delete(real_db_id)
        print(f"Deleted task #{task_id}: '{target_task['name']}'")

def main():
    parser = argparse.ArgumentParser(description="Simple Task CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("name", type=str, help="Task name")
    add_parser.add_argument("-d", "--description", type=str, default="", help="Task description")

    # Subcommand: list
    subparsers.add_parser("list", help="List all tasks")

    # Subcommand: delete
    delete_parser = subparsers.add_parser("delete", help="Delete a task by ID")
    delete_parser.add_argument("id", type=int, help="ID of the task to delete")

    # Subcommand: update
    update_parser = subparsers.add_parser("update", help="Update a task by ID")
    update_parser.add_argument("id", type=int, help="ID of the task to update")
    update_parser.add_argument("-n", "--name", type=str, help="Task name")
    update_parser.add_argument("-d", "--description", type=str, help="Task description")

    args = parser.parse_args()

    # CLI Configs
    db_path = "tasks.db"
    table_name = "tasks"

    init_db(db_path, table_name)

    if args.command == "add":
        add_task(args.name, args.description, db_path, table_name)
    elif args.command == "list":
        list_tasks(db_path, table_name)
    elif args.command == "delete":
        delete_task(args.id, db_path, table_name)
    elif args.command == "update":
        update_task(args.id, args.name, args.description, db_path, table_name)

if __name__ == "__main__":
    main()