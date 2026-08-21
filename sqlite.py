import sqlite3
import re
from typing import Optional

class Sqlite:

    def __init__(self, db_path: str = "database.db", table_name: str = "test"):
        self.db_path = db_path
        self.table_name = self._sanitize_identifier(table_name)
        self.connect = None


    def __enter__(self):
        self.connect = sqlite3.connect(self.db_path)
        self.connect.row_factory = sqlite3.Row
        self.connect.execute("PRAGMA foreign_keys = ON;")
        return self


    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.connect:
            if exc_type is None:
                self.connect.commit()
            else:
                self.connect.rollback()
            self.connect.close()

    @staticmethod
    def _sanitize_identifier(identifier: str) -> str:
        if not isinstance(identifier, str):
            raise TypeError(f"Identifier must be a string, got {type(identifier).__name__}")

        sanitized_identifier = identifier.strip()

        if not re.match(r"^[a-zA-Z0-9_]+$", sanitized_identifier):
            raise TypeError(f"Invalid identifier name detected: '{identifier}'")

        return f'"{sanitized_identifier}"'


    def create_table(self, schema: dict[str, str]):
        col_definitions = []
        for col_name, data_type in schema.items():
            clean_col = self._sanitize_identifier(col_name)
            col_definitions.append(f"{clean_col} {data_type}")
        
        columns_sql = ", ".join(col_definitions)

        query = f"CREATE TABLE IF NOT EXISTS {self.table_name} (id INTEGER PRIMARY KEY AUTOINCREMENT, {columns_sql});"

        self.connect.execute(query)


    def insert(self, data: dict[str, any]) -> int:
        if not data:
            raise ValueError("Data dictionary cannot be empty.")

        clean_cols = [self._sanitize_identifier(col) for col in data.keys()]
        
        columns_sql = ", ".join(clean_cols)
        placeholders = ", ".join(["?"] * len(data))
        values = tuple(data.values())

        query = f"INSERT INTO {self.table_name} ({columns_sql}) VALUES ({placeholders})"

        return self.connect.execute(query, values).lastrowid


    def update(self, record_id: int, data: dict[str, any]) -> bool:
        if not data:
            raise ValueError("Update data dictionary cannot be empty.")

        set_clauses = [f"{self._sanitize_identifier(col)} = ?" for col in data.keys()]
        set_sql = ", ".join(set_clauses)

        values = list(data.values()) + [record_id]

        query = f"UPDATE {self.table_name} SET {set_sql} WHERE id = ?"

        return self.connect.execute(query, values).rowcount > 0


    def get(self, record_id: int) -> Optional[sqlite3.Row]:
        query = f"SELECT * FROM {self.table_name} WHERE id = ?"

        return self.connect.execute(query, (record_id,)).fetchone()


    def get_all(self, limit: Optional[int] = None, offset: Optional[int] = None) -> list[sqlite3.Row]:
        query = f"SELECT * FROM {self.table_name}"
        params = []

        if limit is not None:
            query += " LIMIT ?"
            params.append(limit)
            if offset is not None:
                query += " OFFSET ?"
                params.append(offset)

        return self.connect.execute(query, params).fetchall()


    def delete(self, record_id: int) -> bool:
        query = f"DELETE FROM {self.table_name} WHERE id = ?"

        return self.connect.execute(query, (record_id,)).rowcount > 0
    
