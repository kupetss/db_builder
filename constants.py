ALLOWED_TYPES: set[str] = {"INTEGER", "TEXT", "REAL", "BLOB", "NUMERIC"}

MENU_TEXT: str = (
    "Конструктор баз данных SQLite\n"
    "1) Создать таблицу\n"
    "2) Показать таблицу\n"
    "3) Добавить запись\n"
    "4) Показать содержание таблиц\n"
    "5) Удалить таблицу\n"
    "0) Выход"
)

MENU_MIN: int = 0
MENU_MAX: int = 5