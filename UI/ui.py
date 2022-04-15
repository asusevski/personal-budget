from UI.menu import Menu
from typing import Protocol


class UI(Protocol):
    def initialize_db(self) -> None:
        ...

    def insert_expense_transactions(self) -> None:
        ...

    def insert_income_transactions(self) -> None:
        ...

    def print_table(self, menu: Menu) -> None:
        ...

    def delete_row(self, menu: Menu) -> None:
        ...

    def execute_sql_query(self) -> None:
        ...

    def exit(self) -> None:
        ...
    