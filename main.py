from categories import ExpenseCategory, Account
from interface import find_db, read_incometransaction_from_user, read_transaction_from_user
from manage_database import delete_row, initialize_empty_db, print_table
import sys


def main():
    """
    Interface to create, update, and maintain sqlite database budget.db (default name)

    User can:
        - Initialize basic tables in a budget database
        - Create table in database
        - Insert expenses into expenses table

    """
    while True:
        print("""

        1. Initialize budget database
        2. Insert expenses into expenses table
        3. Insert incomes in incomes table
        4. Print a table
        5. Delete a row from a table
        6. Exit

        """)
        choice = input("Enter your choice: ")

        # Initialize budget database
        if choice == "1":
            database_name = input("Enter database name (default name is budget): ")

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
                payment_name = input("Enter account name (eg: VisaXXXX, Cash, Checking, Bitcoin, etc..) or q if you are done entering accounts: ")
                if payment_name == "" or payment_name.lower() == "q":
                    break
                account_description = input("Enter account description (can be left blank): ")
                account = Account(payment_name, account_description)
                account.insert_into_db(database_name)


            print("""Initializing expense categories...
            
Each category entry will have a category and subcategory.
The category will be a broad categorization and the subcategory, an optional field, 
will be used to make the category more clear (particularly useful for groceries -- one may 
want to have the category be listed as \'groceries\' and the subcategory be \'chicken\', for example).
            
            """)

            while True:
                category_name = input("Enter category name (eg: grocery, bills, etc...) or q if you are done entering expense types: ")
                if category_name == "" or category_name == "q":
                    break
                subcategory = input("Enter subcategory (can be left blank): ")
                expense_category = ExpenseCategory(category_name, subcategory)
                expense_category.insert_into_db(database_name)

        if choice == "2":
            database_name = find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            print("Enter q at any time to stop entering transactions.")
            while True:
                transaction = read_transaction_from_user(database_name)
                if not transaction:
                    print("Transaction cancelled.")
                    break
                else:
                    # Insert transaction into database
                    transaction.execute(database_name)
                    print("Transaction added.")

        if choice == "3":
            database_name = find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            print("Enter q at any time to stop entering income transactions.")
            while True:
                income_transaction = read_incometransaction_from_user(database_name)
                if not income_transaction:
                    print("Transaction cancelled.")
                    break
                else:
                    # Insert transaction into database
                    income_transaction.execute(database_name)
                    print("Transaction added.")
        
        if choice == "4":
            database_name = find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            table_name = input("Enter table name to print: ")
            print_table(database_name, table_name)

        if choice == "5":
            database_name = find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            table_name = input("Enter table from which to delete a row: ")
            print_table(database_name, table_name)
            row_id = input("Enter row id to delete: ")
            delete_row(database_name, table_name, row_id)
            print("Row deleted.")

        # Quit
        if choice == "6":
            sys.exit()


if __name__ == "__main__":
    main()