from Database.database import Database
from UI.menu import Menu
from typing import Protocol


class UI(Protocol):
    def run(self, database: Database) -> None:
        ...

    @staticmethod
    def _initialize_db(db: Database) -> None:
        ...

    def insert_expense_transactions(self,  database: Database) -> None:
        ...

    def insert_income_transactions(self, database: Database) -> None:
        ...

    @staticmethod
    def print_table(menu: Menu, database: Database) -> None:
        ...

    @staticmethod
    def delete_row(menu: Menu, database: Database) -> None:
        ...

    @staticmethod
    def execute_sql_query(database: Database) -> None:
        ...

    @staticmethod
    def exit() -> None:
        ...
    