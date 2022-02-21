from expense_category import ExpenseCategory
from expenses import Expense
from manage_database import initialize_empty_db
#from manage_database import insert_into_table
from manage_database import is_table_empty
from manage_database import print_table
from manage_database import query_db
from ledger import LedgerEntry
from payment_type import PaymentType
from receipt import Receipt
import sys


def main():
    """
    Interface to create, update, and maintain sqlite database budget.db (default name)

    User can:
        - Initialize basic tables in a budget database
        - Create table in database
        - Insert single expense into expenses table
        - Insert receipt of expenses into expenses table

    """
    while True:
        print("""

        1. Initialize budget database
        2. Insert rows into any table
        3. Insert expenses into expenses table
        4. Insert a receipt of expenses into expenses table
        5. Exit

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
            payment_id = 1
            while True:
                payment_name = input("Enter payment name (eg: VisaXXXX, Cash, Checking, Bitcoin, etc..) or q to exit: ")
                if payment_name == "" or payment_name.lower() == "q":
                    break
                payment_description = input("Enter payment description (can be left blank): ")
                payment_type = PaymentType(payment_id, payment_name, payment_description)
                payment_type.insert_into_db(database_name)
                payment_id += 1

            # Enter expense categories:
            print("Initializing expense categories...")
            # NOTE: FIX THIS
            print("Each category entry will have a category and a subcategory.")
            print("The category will be a broad categorization and the subcategory, an optional field, will be \
                used to make the category more clear (particularly useful for groceries -- one may want to \
                have the category be listed as \"groceries\" but have the subcategory be \"bread\" \
                or \"fruits\", for example).")
            category_id = 1
            while True:
                category_name = input("Enter category name (eg: grocery, bills, etc...) or q to exit: ")
                if category_name == "" or category_name == "q":
                    break
                subcategory = input("Enter subcategory (can be left blank): ")
                expense_category = ExpenseCategory(category_id, category_name, subcategory)
                expense_category.insert_into_db(database_name)
                category_id += 1

        if choice == "2":
            print("try later.")

        if choice == "3":
            print("try later.")

        # Enter a receipt of expenses
        if choice == "4":
            database_name = input("Enter database name: ")
            if database_name[-3:] != ".db" or ".sqlite" not in database_name:
                database_name += ".db"
            
            # Get receipt id (select max(id) from receipts + 1)
            # First, checking if the table is empty
            if is_table_empty(database_name, "receipts"):
                receipt_id = 1
            else:
                receipt_id = query_db(database_name, '''SELECT max(id) FROM receipts''')[0][0] + 1
            
            # Get receipt date:
            receipt_date = input("Enter receipt date (YYYY-MM-DD): ")

            # Get receipt location:
            receipt_location = input("Enter receipt location: ")

            # Get expenses from receipt:
            print("Now enter each item on the receipt...")

            # We'll get the recept total by adding up the price for each expense
            receipt_total = 0
            expenses = []
            while True:
                expense_name = input("Enter expense name (or q to exit): ")
                if expense_name == "" or expense_name.lower() == "q":
                    break
                expense_amount = input("Enter expense amount ($): ")

                receipt_total += float(expense_amount)

                expense_type = input("Enter type of expense (want, need, or savings): ")
                print("Select expense category id (see categories below): ")
                print_table(database_name, "expense_categories")
                expense_category_id = input("Enter expense category id: ")

                # Getting expense category:
                query = query_db(database_name, f"SELECT * FROM categories WHERE id = {expense_category_id}")
                expense_category = ExpenseCategory(query[0][0], query[0][1], query[0][2])

                expenses.append([expense_name, expense_amount, expense_type, expense_category])
            
            # Check that the receipt total makes sense:
            print("Total for the receipt is: ${:.2f}".format(receipt_total))
            cmd = input("Enter any button to confirm or q to cancel: ")
            if cmd.lower() == "q":
                break

            # Entering receipt into receipts table and expenses into expense table:
            receipt = Receipt(receipt_id, receipt_date, receipt_location, "{:.2f}".format(receipt_total))
            receipt.insert_into_db(database_name)
            for expense in expenses:
                expense_name = expense[0]
                expense_amount = expense[1]
                expense_type = expense[2]
                expense_category = expense[3]
                expense = Expense(item=expense_name, amount=expense_amount, type=expense_type,\
                    receipt=receipt, category=expense_category)
                expense.insert_into_db(database_name, receipt_id)


            print("How did you pay?")
            while True:
                print("Enter q to exit at any time.")
                print("Select payment id (see payment types below): ")
                print_table(database_name, "payment_types")
                payment_id = input("Enter payment id: ")
                if payment_id == "q":
                    break

                # Getting payment type:
                query = query_db(database_name, f"SELECT * FROM payment_types WHERE id = {payment_id}")
                payment_type = PaymentType(query[0][0], query[0][1], query[0][2])

                print("How much of the receipt did you pay with this payment type?")
                payment_amount = input("Enter payment amount ($): ")
                if payment_amount == "q".lower():
                    break

                # Insert entry into ledger table:
                ledger_entry = LedgerEntry(amount=payment_amount, receipt=receipt, payment_type=payment_type)
                ledger_entry.insert_into_db(database_name, receipt_id)

        # Quit
        if choice == "5":
            sys.exit()


if __name__ == "__main__":
    main()