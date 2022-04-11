from categories import ExpenseCategory, Account
from cli import CLI
from interface import _find_db, read_income_transaction_from_user, read_expense_transaction_from_user
from manage_database import delete_row, initialize_empty_db, print_table, query_db
import sys
# from typing import 


class UI(CLI):
    pass