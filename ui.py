from typing import Protocol


class UI(Protocol):
    def initialize_db(self) -> None:
        ...

    def insert_expense_transaction(self, database_name: str) -> None:
        ...

    def insert_income_transaction(self, database_name: str) -> None:
        ...

    def print_table(self, database_name: str) -> None:
        ...

    def delete_row(self, database_name: str) -> None:
        ...

    def execute_sql_query(self, database_name: str) -> None:
        ...

    def exit(self) -> None:
        ...
    