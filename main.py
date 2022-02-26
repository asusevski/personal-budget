from expense_category import ExpenseCategory
#from expenses import Expense
from interface import find_db
from interface import read_transaction_from_user
from manage_database import initialize_empty_db
#from manage_database import print_table
#from manage_database import query_db
#from ledger import LedgerEntry
from payment_type import PaymentType
#from receipt import Receipt
import sys
#from transactions import Transaction


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
        3. Exit

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
            print("Initializing payment types...")
            while True:
                payment_name = input("Enter payment name (eg: VisaXXXX, Cash, Checking, Bitcoin, etc..) or q to exit: ")
                if payment_name == "" or payment_name.lower() == "q":
                    break
                payment_description = input("Enter payment description (can be left blank): ")
                payment_type = PaymentType(payment_name, payment_description)
                payment_type.insert_into_db(database_name)


            print("""Initializing expense categories...
            
            Each category entry will have a category and subcategory.
            The category will be a broad categorization and the subcategory, an optional field, 
            will be used to make the category more clear (particularly useful for groceries -- one may 
            want to have the category be listed as \'groceries\' and the subcategory be \'chicken\', for example).
            
            """)

            while True:
                category_name = input("Enter category name (eg: grocery, bills, etc...) or q to exit: ")
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

        # Quit
        if choice == "3":
            sys.exit()


if __name__ == "__main__":
    main()