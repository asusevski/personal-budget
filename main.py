from expense_category import ExpenseCategory
from expenses import Expense
from interface import find_db
from manage_database import initialize_empty_db
from manage_database import print_table
#from manage_database import query_db
from ledger import LedgerEntry
from payment_type import PaymentType
from receipt import Receipt
import sys
from transactions import Transaction


# Constants
HST_TAX_RATE = 0.13


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
        2. Insert rows into any table
        3. Insert expenses into expenses table
        4. Exit

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
            print("try later.")

        if choice == "3":
            print("try later.")

        # Enter a receipt of expenses
        if choice == "4":
            database_name = find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

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

                # Check if expense has a discount to apply
                discount = input("Enter any discount amount as a % (or enter to continue with no discount): ")
                if discount != "":
                    discount = float(discount)
                    expense_amount = expense_amount * (1 - (discount/100))
                # Check if expense is taxable:
                taxable = input("Is this expense taxable? (y/n): ")
                if taxable:
                    tax_rate = input("Default tax rate is 13%, enter a different rate (as a %) if desired or enter to continue with 13%: ")
                    if tax_rate == "":
                        tax_rate = HST_TAX_RATE
                    # NOTE: this is not robust to weird input at all, fix!
                    else:
                        tax_rate = float(tax_rate)
                    expense_amount = float(expense_amount) * (1 + tax_rate)
                

                receipt_total += float(expense_amount)

                expense_type = input("Enter type of expense (want, need, or savings): ")
                print(f"Select expense category id for {expense_name} (see categories below): ")
                print_table(database_name, "categories")
                expense_category_id = input(f"Enter expense category id for {expense_name}: ")

                expenses.append([expense_name, expense_amount, expense_type, expense_category_id])
                print("Expense noted.")
                print("-" * 25)
            
            # Check that the receipt total makes sense:
            print("Total for the receipt is: ${:.2f}".format(receipt_total))
            cmd = input("Enter any button to confirm or q to cancel: ")
            if cmd.lower() == "q":
                break

            receipt = Receipt(total="{:.2f}".format(receipt_total), date=receipt_date, location=receipt_location)

            # Inserting receipt into receipts table and have the method return the autoincrement ID
            receipt_id = receipt.insert_into_db(database_name)
            #NOTE!!!!!!: can ONLY get receipt id by runnning receipt.insert_into_db(database_name), 
            # so how can I initialize a transaction object and also run receipt_id?
            # expenses = []
            for expense in expenses:
                expense_name = expense[0]
                expense_amount = expense[1]
                expense_type = expense[2]
                expense_category_id = expense[3]
                expense = Expense(item=expense_name, amount=expense_amount, type=expense_type,\
                    receipt_id=receipt_id, category_id=expense_category_id)
                expense.insert_into_db(database_name)

            print("How did you pay?")
            tol = 10e-4
            while abs(receipt_total) >= tol:
                print("Remaining on receipt: ${:.2f}".format(receipt_total))
                print("Select payment id used to pay (see payment types below): ")
                print_table(database_name, "payment_types")
                payment_type_id = input("Enter payment id (or q to exit): ")
                if payment_type_id.lower() == "q":
                    break
                
                print("How much of the receipt did you pay with this payment type?")
                payment_amount = input("Enter payment amount ($): ")
                if payment_amount.lower() == "q":
                    break
                
                ledger_entry = LedgerEntry(amount=payment_amount, receipt_id=receipt_id, payment_type_id=payment_type_id)
                ledger_entry.insert_into_db(database_name)
                receipt_total -= float(payment_amount)

        # Quit
        if choice == "4":
            sys.exit()


if __name__ == "__main__":
    main()