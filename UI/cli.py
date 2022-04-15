from Transactions.categories import Account, ExpenseCategory
from Database.manage_database import delete_row, initialize_empty_db, print_table, query_db
from UI.menu import Menu
import sys
from UI.cli_helpers import _find_db, _read_expense_transaction_from_user, _read_income_transaction_from_user


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

    def insert_expense_transactions(self) -> None:
        database_name = _find_db()
        if not database_name:
            print("No database found. Please intialize a database first.")

        print("Enter q at any time to stop entering transactions.")
        while True:
            expense_transaction = _read_expense_transaction_from_user(database_name)
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

    def insert_income_transactions(self) -> None:
        database_name = _find_db()
        if not database_name:
            print("No database found. Please intialize a database first.")
            return

        print("Enter q at any time to stop entering income transactions.")
        while True:
            income_transaction = _read_income_transaction_from_user(database_name)
            if not income_transaction:
                print("Transaction cancelled.")
                break
            else:
                # Insert transaction into database
                retval = income_transaction.execute(database_name)
                if not retval:
                    print("Income transaction added.")
                else:
                    print(f"Income transaction failed to be added. Error message: {retval}")
    
    def print_table(self, menu: Menu) -> None:
        database_name = _find_db()
        if not database_name:
            print("No database found. Please intialize a database first.")
            return

        table_name = menu.run()

        print_table(database_name, table_name)

    def delete_row(self, menu: Menu) -> None:
        database_name = _find_db()
        if not database_name:
            print("No database found. Please intialize a database first.")
            return

        table_name, row_id = menu.run(database_name)

        delete_row(database_name, table_name, row_id)
        print("Row deleted.")

    def execute_sql_query(self) -> None:
        database_name = _find_db()
        if not database_name:
            print("No database found. Please intialize a database first.")
            return

        print("Enter SQL query: ")
        sql_query = input("> ")
        print("Executing query...")
        vals = query_db(database_name, sql_query)
        print(f"Results: {vals}")

    def exit(self) -> None:
        sys.exit(0)
