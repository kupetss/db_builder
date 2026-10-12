import sqlite3
from pathlib import Path
from typing import Any

from errors import DatabaseError
from constants import ALLOWED_TYPES


class SQLiteBackend:
    def __init__(self, db_path: str | Path) -> None:
        self.db_path = Path(db_path)

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.db_path)
        return connection

    @staticmethod
    def _quote_identifier(name: str) -> str:
        if not name or not name.replace("_", "").isalnum():
            raise DatabaseError(f"Недопустимое имя '{name}'. Используйте буквы и цифры")
        return f'"{name}"'

    def table_exists(self, table_name: str) -> bool:
        with self._connect() as connection:
            cur = connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type = 'table' AND name = ?",
                (table_name,),
            )
            return cur.fetchone() is not None

    def list_tables(self) -> list[str]:
        with self._connect() as connection:
            cur = connection.execute(
                "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name"
            )
            return [row[0] for row in cur.fetchall()]

    def create_table(self, table_name: str, columns: list[tuple[str, str]]) -> None:
        if not columns:
            raise DatabaseError("Нельзя создавать таблицу без столбцов")

        if self.table_exists(table_name):
            raise DatabaseError(f"Таблица {table_name} уже существует")

        cols_sql = ", ".join(
            f"{self._quote_identifier(col)} {col_type}"
            for col, col_type in columns
        )
        query = f"CREATE TABLE {self._quote_identifier(table_name)} ({cols_sql});"

        with self._connect() as connection:
            connection.execute(query)

    def get_columns(self, table_name: str) -> list[str]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблицы '{table_name}' не существует")

        with self._connect() as connection:
            cur = connection.execute(
                f"PRAGMA table_info({self._quote_identifier(table_name)});"
            )
            return [row[1] for row in cur.fetchall()]

    def insert_row(self, table_name: str, values: list[Any]) -> None:
        columns = self.get_columns(table_name)

        if len(values) != len(columns):
            raise DatabaseError(
                f"Ожидалось {len(columns)} значений, получено {len(values)}"
            )

        placeholders = ", ".join("?" for _ in values)
        cols_sql = ", ".join(self._quote_identifier(c) for c in columns)
        query = (
            f"INSERT INTO {self._quote_identifier(table_name)} "
            f"({cols_sql}) VALUES ({placeholders});"
        )

        with self._connect() as connection:
            connection.execute(query, values)

    def fetch_all(self, table_name: str) -> tuple[list[str], list[tuple[Any, ...]]]:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблицы {table_name} не существует")

        with self._connect() as connection:
            cur = connection.execute(
                f"SELECT * FROM {self._quote_identifier(table_name)};"
            )
            columns = [desc[0] for desc in cur.description] if cur.description else []
            rows = cur.fetchall()

        return columns, rows

    def delete_table(self, table_name: str) -> None:
        if not self.table_exists(table_name):
            raise DatabaseError(f"Таблицы {table_name} не существует")

        with self._connect() as connection:
            connection.execute(f"DROP TABLE {self._quote_identifier(table_name)};")