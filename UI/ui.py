from Database.database import Database
from UI.menu import Menu
from typing import Protocol


class UI(Protocol):
    def run(self) -> None:
        ...

    def _initialize_db(self) -> None:
        ...

    def insert_expense_transactions(self,  database: Database) -> None:
        ...

    def insert_income_transactions(self, database: Database) -> None:
        ...

    def print_table(self, menu: Menu) -> None:
        ...

    def delete_row(self, menu: Menu) -> None:
        ...

    def execute_sql_query(self) -> None:
        ...

    def exit(self) -> None:
        ...
    