import argparse
from sqlite import Sqlite

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
        print(f"Task created with ID: {task_id}")

def list_tasks(db_path: str, table_name: str):
    with Sqlite(db_path, table_name) as db:
        tasks = db.get_all()
        if not tasks:
            print("No tasks found.")
            return
        for task in tasks:
            print(f"[{task['id']}] {task['name']} - {task['description']}")

def main():
    parser = argparse.ArgumentParser(description="Simple Task CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Subcommand: add
    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("name", type=str, help="Task name")
    add_parser.add_argument("-d", "--description", type=str, default="", help="Task description")

    # Subcommand: list
    subparsers.add_parser("list", help="List all tasks")

    args = parser.parse_args()

    # CLI Configs
    db_path = "tasks.db"
    table_name = "tasks"

    init_db(db_path, table_name)

    if args.command == "add":
        add_task(args.name, args.description, db_path, table_name)
    elif args.command == "list":
        list_tasks(db_path, table_name)

if __name__ == "__main__":
    main()