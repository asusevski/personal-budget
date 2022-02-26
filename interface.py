from expense_category import ExpenseCategory
from expenses import Expense
from ledger import LedgerEntry
from manage_database import print_table
from manage_database import search_category
from manage_database import search_expense
import os
import re
from payment_type import PaymentType
from receipt import Receipt
from transactions import Transaction


# CONSTANTS
HST_TAX_RATE = 0.13


def find_db() -> str:
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


def read_expense_category_from_user() -> ExpenseCategory:
    """
    Reads an expense category from the user.

    Returns:
        An ExpenseCategory object.
    """    
    name = input("Enter expense category name: ")
    description = input("Enter expense category description: ")
    expense_category = ExpenseCategory(name, description)
    return expense_category


def read_payment_type_from_user() -> PaymentType:
    """
    Reads a payment type from the user.

    Returns:
        A PaymentType object.
    """
    name = input("Enter payment type name: ")
    description = input("Enter payment type description: ")
    payment_type = PaymentType(name, description)
    return payment_type


def read_user_receipt() -> list:
    """
    Reads all data required from user to initialize a receipt object.

    Arguments:
        database_name: The name of the database to use.

    Returns:
        Either a list of the following:
            receipt_date: The date of the receipt.
            receipt_location: The location of the receipt.
        Or None if the user quits early.

    """
    # Get receipt date:
    receipt_date = input("Enter date of expense or expenses (YYYY-MM-DD): ")
    if receipt_date.lower() == "q":
        return None

    # Get receipt location:
    receipt_location = input("Enter location of expense(s): ")
    if receipt_location.lower() == "q":
        return None
    return [receipt_date, receipt_location]


def apply_discount_and_tax(expense_amount: str) -> str:
    expense_amount = float(expense_amount)
    # Check if expense has a discount to apply
    discount = input("Enter any discount amount as a % (or enter to continue with no discount): ")
    if discount.lower() == "q":
        return None
    if discount != "":
        discount = float(discount)
        expense_amount = expense_amount * (1 - (discount/100))

    # Check if expense is taxable:
    taxable = input("Is this expense taxable? (y/n): ")
    if taxable.lower() == "q":
        return None
    if taxable:
        tax_rate = input("Default tax rate is 13%, enter a different rate (as a %) if desired or enter to continue with 13%: ")
        if tax_rate.lower() == "q":
            return None
        if tax_rate == "":
            tax_rate = HST_TAX_RATE
        # NOTE: this is not robust to weird input at all, fix!
        else:
            tax_rate = float(tax_rate)
        expense_amount = float(expense_amount) * (1 + tax_rate)
    # format expense amount to 2 decimal places and return
    return "{:.2f}".format(expense_amount)


def read_user_expenses(database_name: str) -> list:
    """
    Reads all data required from user to initialize an expense object.

    Specifically, reads in the expense name, amount, type, details, and category id.

    Arguments:
        database_name: The name of the database to use.

    Returns:
        Either a list of the following:
            expense_name: The name of the expense.
            expense_amount: The amount of the expense.
            expense_type: The type of the expense.
            expense_details: Any details about the expense.
            expense_category_id: The category id of the expense.
        Or None if the user quits early.

    """
    # Get expense name:
    expense_name = input("Enter expense name: ")
    if expense_name.lower() == "q":
        return None

    # Get expense amount:
    expense_amount = input("Enter expense amount ($): ")
    if expense_amount.lower() == "q":
        return None

    expenses = []
    while True:
        expense_name = input("Enter expense name (enter nothing or \"done\" if done entering expenses): ")
        if expense_name.lower() == "q":
            return None
        if expense_name == "" or expense_name == "done":
            break

        # Search to see if this expense has been entered before. If it has, ask for confirmation from user to reuse values.
        expense_table, existing_expense = search_expense(database_name, expense_name)
        if existing_expense:
            print("Found a prior expense entered with the same name. Is this the same expense we are entering?")
            print("Existing expense: ")
            print(expense_table)
            existing_expense_category = existing_expense[-1]
            category_table, _ = search_category(database_name, existing_expense_category)
            print("Existing expense category: ")
            print(category_table)
            same_expense = input("Same item (you will be given the chance to confirm the amount, details, and type of the expense)? (y/n): ")
            if same_expense.lower() == "y":
                expense_name = existing_expense[1]

                # Confirm expense amount:
                amount_confirm = input(f"If {existing_expense[2]} is the correct price, press enter. Otherwise, input correct price ($): ")
                if amount_confirm == "q":
                    return None
                if amount_confirm != "":
                    expense_amount = amount_confirm
                else:
                    expense_amount = existing_expense[2]
                    expense_amount = apply_discount_and_tax(expense_amount)
                    if not expense_amount:
                        return None

                # Confirm expense type:
                type_confirm = input(f"If {existing_expense[3]} is the correct type, press enter. Otherwise, input correct type: ")
                if type_confirm == "q":
                    return None
                if type_confirm != "":
                    expense_type = type_confirm
                else:
                    expense_type = existing_expense[3]

                expense_category = existing_expense_category
                expense_details = input("Enter any details about the expense (or enter to continue with no details): ")
                if expense_details.lower() == "q":
                    return None
                expenses.append([expense_name, expense_amount, expense_type, expense_details, expense_category])

        # If there are no existing expenses or the expense is not the same as the existing expense, ask for expense details.
        else:
            expense_amount = input("Enter expense amount ($): ")
            if expense_amount.lower() == "q":
                return None

            expense_amount = apply_discount_and_tax(expense_amount)

            expense_type = input("Enter type of expense (want, need, or savings): ")
            if expense_type.lower() == "q":
                return None

            expense_details = input("Enter any details about the expense (or enter to continue with no details): ")
            if expense_details.lower() == "q":
                return None

            print(f"Select expense category id for {expense_name} (see categories below): ")
            print_table(database_name, "categories")
            expense_category = input(f"Enter expense category id for {expense_name}: ")
            if expense_category.lower() == "q":
                return None
            expenses.append([expense_name, expense_amount, expense_type, expense_details, expense_category])
    return expenses


def read_user_ledger_entries(database_name: str, receipt_total: float) -> list:
    print("How did you pay?")
    tol = 10e-4
    ledger_entries = []
    while abs(receipt_total) >= tol:
        print("Remaining on receipt: ${:.2f}".format(receipt_total))
        print("Select payment id used to pay (see payment types below): ")
        print_table(database_name, "payment_types")
        payment_type_id = input("Enter payment id: ")
        if payment_type_id.lower() == "q":
            return None
        
        print("How much of the receipt did you pay with this payment type?")
        payment_amount = input("Enter payment amount ($): ")
        if payment_amount.lower() == "q":
            return None
        
        ledger_entries.append(payment_amount, payment_type_id)
    return ledger_entries


def read_transaction_from_user(database_name: str) -> Transaction:
    """
    Reads a transaction from the user.

    Arguments:
        database_name: The name of the database to use.

    Returns:
        A Transaction object or None if the user ends input early with 'q' input.

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
    for expense in expense_user_data:
        expense_name = expense[0]
        expense_amount = expense[1]
        expense_type = expense[2]
        expense_details = expense[3]
        expense_category = expense[4]
        expense = Expense(item=expense_name, amount=expense_amount, type=expense_type,\
                          details=expense_details, receipt=receipt, category_id=expense_category)
        expenses.append(expense)
    
    ledger_entries = []
    for ledger_entry in ledger_entries_user_data:
        payment_amount = ledger_entry[0]
        payment_type_id = ledger_entry[1]
        ledger_entry = LedgerEntry(amount=payment_amount, receipt=receipt, payment_type_id=payment_type_id)
        ledger_entries.append(ledger_entry)

    transaction = Transaction(receipt=receipt, expenses=expenses, ledger_entries=ledger_entries)
    return transaction
