from categories import ExpenseCategory, Account
from cli import CLI
from interface import read_income_transaction_from_user, read_expense_transaction_from_user
from manage_database import delete_row, initialize_empty_db, print_table, query_db
from menu import Menu
import os
import re
from typing import Any, Protocol


# Should we do something like this for the menu?
#class MenuSource(Protocol):
#    def run(self) -> None:
#        ...


def _find_db() -> str:
    """
    Finds and returns the name of the database to use.

    A database must end in '.db' or '.sqlite3' and must be in the same directory as this file.

    Returns:
        The name of the database to use (or the empty string if no database is found).
    """
    db_regex = re.compile(r'(.*)(\.db|\.sqlite3)$')
    files = sorted(os.listdir('.'))
    matches = list(filter(lambda x: db_regex.match(x), files))
    if len(matches) == 0:
        return ""
    else:
        return matches[0]


class UI(Protocol):
    def user_menu_selection(self, menu: Menu) -> Any:
        menu.run()

    def initialize_db(self)
    