1)     def __init__(self, db_path: str | Path) -> None:

2)     def _connect(self) -> sqlite3.Connection:

3) "SELECT name FROM sqlite_master "
                "WHERE type='table' AND name NOT LIKE 'sqlite_%' "
                "ORDER BY name;"

4) cols_sql = ", ".join(
            f"{self._quote_identifier(col)} {col_type}"
            for col, col_type in columns
        )

5) 