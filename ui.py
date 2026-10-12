from __future__ import annotations

import sqlite3
from pathlib import Path

from backend import SQLiteBackend
from errors import DatabaseError
from constants import (
    ALLOWED_TYPES,
    MENU_TEXT,
    MENU_MIN,
    MENU_MAX,
)


class ConsoleUI:
    def __init__(self) -> None:
        self.backend: SQLiteBackend | None = None

    @staticmethod
    def _ask(prompt: str) -> str:
        return input(prompt).strip()

    @staticmethod
    def _ask_int(prompt: str, min_val: int, max_val: int) -> int | None:
        raw = input(prompt).strip()

        if not raw:
            return None

        try:
            value = int(raw)
        except ValueError:
            print("  ! Нужно ввести целое число")
            return None

        if not (min_val <= value <= max_val):
            print(f"  ! Число должно быть в диапазоне {min_val}...{max_val}")
            return None

        return value

    def _require_backend(self) -> SQLiteBackend | None:
        if self.backend is None:
            print("  ! Сначала выберите или создайте базу данных")
        return self.backend

    def choose_database(self) -> None:
        name = self._ask("Имя файла базы данных (без .db): ")

        if not name:
            print("  ! Имя не может быть пустым")
            return

        db_path = Path(f"{name}.db")
        self.backend = SQLiteBackend(db_path)
        print(f"  ✓ База данных: {db_path.resolve()}")

    def create_table(self) -> None:
        backend = self._require_backend()
        if backend is None:
            return

        table_name = self._ask("Имя новой таблицы: ")
        if not table_name:
            print("  ! Имя не может быть пустым")
            return

        columns: list[tuple[str, str]] = []

        print("  Введите столбцы в формате: имя ТИП")
        print(f"  Доступные типы: {', '.join(sorted(ALLOWED_TYPES))}")
        print("  Пустая строка - закончить ввод")

        while True:
            raw = self._ask(f"  Столбец #{len(columns) + 1}: ")

            if not raw:
                break

            parts = raw.split()
            if len(parts) != 2:
                print("  ! Формат: <имя> <ТИП>")
                continue

            col_name, col_type = parts[0], parts[1].upper()

            if col_type not in ALLOWED_TYPES:
                print(f"  ! Неизвестный тип '{col_type}'")
                continue

            columns.append((col_name, col_type))

        try:
            backend.create_table(table_name, columns)
        except DatabaseError as exc:
            print(f"  ! Ошибка: {exc}")
            return

        print(f"  ✓ Таблица '{table_name}' создана ({len(columns)} столбцов)")

    def show_tables(self) -> None:
        backend = self._require_backend()
        if backend is None:
            return

        tables = backend.list_tables()

        if not tables:
            print("  (в базе нет таблиц)")
            return

        print("  Таблицы в базе:")
        for i, name in enumerate(tables, 1):
            print(f"    {i}. {name}")

    def insert_row(self) -> None:
        backend = self._require_backend()
        if backend is None:
            return

        table_name = self._ask("Имя таблицы: ")

        try:
            columns = backend.get_columns(table_name)
        except DatabaseError as exc:
            print(f"  ! Ошибка: {exc}")
            return

        print(f"  Столбцы: {', '.join(columns)}")

        values: list[str] = []
        for col in columns:
            values.append(input(f"    {col} = ").strip())

        try:
            backend.insert_row(table_name, values)
        except (DatabaseError, sqlite3.Error) as exc:
            print(f"  ! Ошибка: {exc}")
            return

        print("  ✓ Запись добавлена")

    def show_table_content(self) -> None:
        backend = self._require_backend()
        if backend is None:
            return

        table_name = self._ask("Имя таблицы: ")

        try:
            columns, rows = backend.fetch_all(table_name)
        except DatabaseError as exc:
            print(f"  ! Ошибка: {exc}")
            return

        if not rows:
            print("  (таблица пуста)")
            return

        widths = [len(c) for c in columns]
        for row in rows:
            for i, cell in enumerate(row):
                widths[i] = max(widths[i], len(str(cell)))

        sep = "+-" + "-+-".join("-" * w for w in widths) + "-+"

        header = "| " + " | ".join(
            c.ljust(w) for c, w in zip(columns, widths)
        ) + " |"

        print(sep)
        print(header)
        print(sep)
        for row in rows:
            line = "| " + " | ".join(
                str(cell).ljust(w) for cell, w in zip(row, widths)
            ) + " |"
            print(line)
        print(sep)

        print(f"  Всего строк: {len(rows)}")

    def delete_table(self) -> None:
        backend = self._require_backend()
        if backend is None:
            return

        table_name = self._ask("Имя таблицы для удаления: ")

        confirm = self._ask(
            f"  Удалить '{table_name}' безвозвратно? (yes/no): "
        ).lower()

        if confirm != "yes":
            print("  Отменено")
            return

        try:
            backend.delete_table(table_name)
        except DatabaseError as exc:
            print(f"  ! Ошибка: {exc}")
            return

        print(f"  ✓ Таблица '{table_name}' удалена")

    def run(self) -> None:
        self.choose_database()

        actions = {
            1: self.create_table,
            2: self.show_tables,
            3: self.insert_row,
            4: self.show_table_content,
            5: self.delete_table,
        }

        while True:
            print(MENU_TEXT)

            choice = self._ask_int("Ваш выбор: ", MENU_MIN, MENU_MAX)

            if choice is None:
                continue

            if choice == 0:
                print("До встречи!")
                return

            action = actions.get(choice)
            if action is not None:
                try:
                    action()
                except sqlite3.Error as exc:
                    print(f"  ! Ошибка SQLite: {exc}")
                except KeyboardInterrupt:
                    print("\n  Прервано пользователем")