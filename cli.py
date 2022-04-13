from categories import Account, ExpenseCategory
from expenses import Expense, LedgerEntry, Receipt
from incomes import Income, Paystub, PaystubLedger
from manage_database import delete_row, initialize_empty_db, print_table, query_db
import os
import re
import sys
from transactions import ExpenseTransaction, IncomeTransaction


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


def read_expense_transaction_from_user(database_name: str) -> ExpenseTransaction:
    """
    Reads an expense transaction from the user.

    Arguments:
        database_name: The name of the database to use.

    Returns:
        A ExpenseTransaction object or None if the user ends input early with 'q' input.

    """
    receipt_user_data = read_user_receipt()
    if not receipt_user_data:
        return None

    expense_user_data = read_user_expenses(database_name)
    if not expense_user_data:
        return None

    # Calculate receipt total:
    receipt_total = 0
    for expense in expense_user_data:
        amount = float(expense[1])
        receipt_total += amount
    
    ledger_entries_user_data = read_user_ledger_entries(database_name, receipt_total)
    if not ledger_entries_user_data:
        return None
    
    receipt_date = receipt_user_data[0]
    receipt_location = receipt_user_data[1]

    receipt = Receipt(total="{:.2f}".format(receipt_total), date=receipt_date, location=receipt_location)

    expenses = []
    for exp in expense_user_data:
        expense_name = exp[0]
        expense_amount = exp[1]
        expense_type = exp[2]
        expense_details = exp[3]
        expense_category = exp[4]
        expense = Expense(item=expense_name, amount=expense_amount, type=expense_type,\
                          details=expense_details, receipt=receipt, category_id=expense_category)
        expenses.append(expense)
    
    ledger_entries = []
    for ledger_entry in ledger_entries_user_data:
        payment_amount = ledger_entry[0]
        account_id = ledger_entry[1]
        ledger_entry = LedgerEntry(amount=payment_amount, receipt=receipt, account_id=account_id)
        ledger_entries.append(ledger_entry)

    expense_transaction = ExpenseTransaction(receipt=receipt, expenses=expenses, ledger_entries=ledger_entries)
    return expense_transaction


class CLI():
    def initialize_db(self) -> None:
        # Initialize budget database
        print("Enter database name (default name is budget): ")
        database_name = input("> ")

        # If no custome database name is entered, use default name
        if database_name == "":
            database_name = "budget"

        # Adding suffix to database name
        if database_name[-3:] != ".db" or ".sqlite" not in database_name:
            database_name += ".db"

        # Initialize empty database
        initialize_empty_db(database_name)

        # Enter payment types:
        print("Initializing accounts...")
        while True:
            print("Enter account name (eg: VisaXXXX, Cash, Checking, Bitcoin, etc..) or q if you are done entering accounts: ")
            payment_name = input("> ")
            if payment_name == "" or payment_name.lower() == "q":
                break
            print("Enter account description (can be left blank): ")
            account_description = input("> ")
            account = Account(payment_name, account_description)
            account.insert_into_db(database_name)


        print("""Initializing expense categories...
        
Each category entry will have a category and subcategory.
The category will be a broad categorization and the subcategory, an optional field, 
will be used to make the category more clear (particularly useful for groceries -- one may 
want to have the category be listed as \'groceries\' and the subcategory be \'chicken\', for example).
        
        """)

        while True:
            print("Enter category name (eg: grocery, bills, etc...) or q if you are done entering expense types: ")
            category_name = input("> ")
            if category_name == "" or category_name == "q":
                break
            print("Enter subcategory (can be left blank): ")
            subcategory = input("> ")
            expense_category = ExpenseCategory(category_name, subcategory)
            expense_category.insert_into_db(database_name)

    def insert_expense_transactions(self, database_name: str) -> None:
        database_name = _find_db()
        if not database_name:
            print("No database found. Please intialize a database first.")

        print("Enter q at any time to stop entering transactions.")
        while True:
            expense_transaction = read_expense_transaction_from_user(database_name)
            if not expense_transaction:
                print("Transaction cancelled.")
                break
            else:
                # Insert transaction into database
                retval = expense_transaction.execute(database_name)
                if not retval:
                    print("Transaction added to database.")
                else:
                    print(f"Transaction failed to be added. Error message: {retval}")
    
    def exit(self) -> None:
        sys.exit(0)
