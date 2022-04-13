from categories import Account, ExpenseCategory
from expenses import Expense, LedgerEntry, Receipt
from incomes import Income, Paystub, PaystubLedger
from manage_database import print_table, search_category, search_expense
import os
import re
from transactions import IncomeTransaction, ExpenseTransaction


# CONSTANTS
HST_TAX_RATE = 0.13


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


def _read_expense_category_from_user() -> ExpenseCategory:
    """
    Reads an expense category from the user.

    Returns:
        An ExpenseCategory object.
    """    
    print("Enter expense category name: ")
    name = input("> ")
    print("Enter expense category description: ")
    description = input("> ")
    expense_category = ExpenseCategory(name, description)
    return expense_category


def _read_account_from_user() -> Account:
    """
    Reads a payment type from the user.

    Returns:
        An Account object.
    """
    print("Enter payment type name: ")
    name = input("> ")
    print("Enter payment type description: ")
    description = input("> ")
    account = Account(name, description)
    return account


def _read_user_receipt() -> list:
    """
    Reads all data required from user to initialize a receipt object.

    Returns:
        Either a list of the following:
            receipt_date: The date of the receipt.
            receipt_location: The location of the receipt.
        Or None if the user quits early.

    """
    # Get receipt date:
    print("Enter date of expense or expenses (YYYY-MM-DD): ")
    receipt_date = input("> ")
    if receipt_date.lower() == "q":
        return None

    # Get receipt location:
    print("Enter location of expense(s): ")
    receipt_location = input("> ")
    if receipt_location.lower() == "q":
        return None
    return [receipt_date, receipt_location]


def _apply_tax(expense_amount: str) -> str:
    expense_amount = float(expense_amount)

    # Check if expense is taxable:
    print("Is this expense taxable? (y/n): ")
    taxable = input("> ")
    if taxable.lower() == "q":
        return None
    if taxable.lower() == "y":
        print("Default tax rate is 13%, enter a different rate (as a %) if desired or enter to continue with 13%: ")
        tax_rate = input("> ")
        if tax_rate.lower() == "q":
            return None
        if tax_rate == "":
            tax_rate = HST_TAX_RATE
        # NOTE: this is not robust to weird input at all, fix!
        else:
            tax_rate = float(tax_rate) / 100
        expense_amount = float(expense_amount) * (1 + tax_rate)
    # format expense amount to 2 decimal places and return
    return "{:.2f}".format(expense_amount)


def _cycle_suggestions(possible_vals: list, col_name: str) -> str:
    idx = 0
    while True:
        print(f"Is \"{possible_vals[idx]}\" the entry for the column \"{col_name}\" you want to add?")
        print("Press enter to confirm suggestion, \'n\' to see the next suggestion, \'exit\' to exit and ignore suggestions, and anything else to enter a custom entry: ")
        cmd = input("> ")
        if cmd.lower() == "":
            return str(possible_vals[idx])
        elif cmd.lower() == "n":
            idx = (idx + 1) % len(possible_vals)
        elif cmd.lower() == "exit":
            return "exit"
        else:
            return cmd


def _read_expense_name() -> str:
    print("Enter expense name (enter nothing or \"done\" if done entering expenses): ")
    expense_name = input("> ")
    if expense_name.lower() == "q":
        return None
    if expense_name == "" or expense_name == "done":
        return "done"
    return expense_name


def _read_expense_amount() -> str:
    print("Enter expense amount ($): ")
    expense_amount = input("> ")
    if expense_amount.lower() == "q":
        return None

    expense_amount = _apply_tax(expense_amount)
    if not expense_amount:
        return None

    return expense_amount


def _read_expense_type() -> str:
    print("Enter type of expense (want, need, or savings): ")
    expense_type = input("> ")
    if expense_type.lower() == "q":
        return None
    return expense_type


def _read_expense_details() -> str:
    print("Enter any details about the expense (or enter to continue with no details): ")
    expense_details = input("> ")
    if expense_details.lower() == "q":
        return None
    return expense_details


def _read_expense_category(database_name: str, expense_name: str) -> str:
    print(f"Select expense category id for {expense_name} (see categories below): ")
    print_table(database_name, "categories")
    print(f"Enter expense category id for {expense_name} or enter \"add\" to add a new expense category for this expense: ")
    expense_category_id = input("> ")
    if expense_category_id.lower() == "q":
        return None
    if expense_category_id.lower() == "add":
        print("Enter new expense category name: ")
        expense_category_name = input("> ")
        print("Enter expense subcategory name (or enter to continue with no subcategory): ")
        expense_subcategory = input("> ")
        expense_cat = ExpenseCategory(expense_category_name, expense_subcategory)
        expense_category_id = expense_cat.insert_into_db(database_name)
    return expense_category_id


def _read_user_expenses_no_suggestions(database_name: str, **kwargs) -> list:
    """
    Reads all data required from user to initialize an expense object.

    Specifically, reads in the expense name, amount, type, details, and category id.

    Arguments:
        database_name: The name of the database to use.
        kwargs: A dictionary of already queried items.

    Returns:
        Either a list of the following:
            expense_name: The name of the expense.
            expense_amount: The amount of the expense.
            expense_type: The type of the expense.
            expense_details: Any details about the expense.
            expense_category_id: The category id of the expense.
        Or None if the user quits early.

    """
    expense = []
    if "expense_name" not in kwargs:
        expense_name = _read_expense_name()
        if not expense_name or expense_name == "done":
            return None
        expense.append(expense_name)
    else:
        expense.append(kwargs["expense_name"])

    if "expense_amount" not in kwargs:
        expense_amount = _read_expense_amount()
        if not expense_amount:
            return None
        expense.append(expense_amount)
    else:
        expense.append(kwargs["expense_amount"])

    if "expense_type" not in kwargs:
        expense_type = _read_expense_type()
        if not expense_type:
            return None
        expense.append(expense_type)
    else:
        expense.append(kwargs["expense_type"])

    if "expense_details" not in kwargs:
        expense_details = _read_expense_details()
        # Expense details is optional, so empty string is valid. Thus, need to check if we have None or empty string.
        if expense_details is None:
            return None
        expense.append(expense_details)
    else:
        expense.append(kwargs["expense_details"])

    if "expense_category_id" not in kwargs:
        # It's possible there's no local variable expense_name, so we just grab it from the expense list.
        expense_category_id = _read_expense_category(database_name, expense[0])
        if not expense_category_id:
            return None
        expense.append(expense_category_id)
    else:
        expense.append(kwargs["expense_category_id"])

    return expense


def _read_user_expenses(database_name: str) -> list:
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
    expenses = []
    while True:
        expense_name = _read_expense_name()
        if not expense_name:
            return None
        if expense_name == "done":
            break
        
        # Search for similar expense names
        _, vals = search_expense(database_name, expense_name)
        if vals:
            print("We found an existing entry with a similar name.")
            possible_item_names = [val[1] for val in vals]
            expense_name_suggestion = _cycle_suggestions(possible_item_names, "expense_name")
            if expense_name_suggestion.lower() == "q": # Early quit
                return None
            elif expense_name_suggestion == "exit": # Ignore suggestions
                expense = _read_user_expenses_no_suggestions(database_name, expense_name=expense_name)
                if not expense:
                    return None
                expenses.append(expense)
                continue
            else:
                expense_name = expense_name_suggestion
            

            possible_amounts = [val[2] for val in vals]
            expense_amount_suggestion = _cycle_suggestions(possible_amounts, "amount")
            if expense_amount_suggestion.lower() == "q": # Early quit
                return None
            elif expense_amount_suggestion == "exit": # Ignore suggestions
                expense = _read_user_expenses_no_suggestions(database_name, expense_name=expense_name)
                if not expense:
                    return None
                expenses.append(expense)
                continue
            else:
                expense_amount = expense_amount_suggestion
            
            possible_types = list(dict.fromkeys([val[3] for val in vals]))
            expense_type_suggestion = _cycle_suggestions(possible_types, "type")
            if expense_type_suggestion.lower() == "q": # Early quit
                return None
            elif expense_type_suggestion == "exit": # Ignore suggestions
                expense = _read_user_expenses_no_suggestions(database_name, expense_name=expense_name, \
                    expense_amount=expense_amount)
                if not expense:
                    return None
                expenses.append(expense)
                continue
            else:
                expense_type = expense_type_suggestion
            
            # For category ids, we need more info since the value is acutally an ID rather than a name that's recognizable to the user.
            possible_category_ids = list(dict.fromkeys([val[5] for val in vals]))
            possible_categories = []
            for possible_category_id in possible_category_ids:
                _, category_vals = search_category(database_name, possible_category_id)
                # category_vals is a list instead of a list of tuples since it only ever returns 1 row from table
                category_name = category_vals[1]
                subcategory_name = category_vals[2]
                # NOTE: not sure this works
                if not subcategory_name:
                    possible_categories.append(f"{category_name}")
                else:
                    possible_categories.append(f"{category_name}-{subcategory_name}")
            expense_category_suggestion = _cycle_suggestions(possible_categories, "category")

            if expense_category_suggestion.lower() == "q": # Early quit
                return None
            elif expense_category_suggestion == "exit": # Ignore suggestions
                expense = _read_user_expenses_no_suggestions(database_name, expense_name=expense_name, \
                    expense_amount=expense_amount, expense_type=expense_type)
                if not expense:
                    return None
                expenses.append(expense)
                continue
            else:
                expense_category_id = possible_category_ids[possible_categories.index(expense_category_suggestion)]

            # Expense details is optional, so empty string is valid. Thus, need to check if we have None or empty string.
            expense_details = _read_expense_details()
            if expense_details is None:
                return None
            
            expenses.append([expense_name, expense_amount, expense_type, expense_details, expense_category_id])
            print("Expense recorded.")

        else:
            expense = _read_user_expenses_no_suggestions(database_name, expense_name=expense_name)
            expenses.append(expense)
            print("Expense recorded.")
    return expenses


def _read_user_ledger_entries(database_name: str, receipt_total: float) -> list:
    print("How did you pay?")
    tol = 10e-4
    ledger_entries = []
    while abs(receipt_total) >= tol:
        print("Remaining on receipt: ${:.2f}".format(receipt_total))
        print("Select account id used to pay (see accounts below): ")
        print_table(database_name, "accounts")
        print("Enter account id or enter \"add\" to add a new account: ")
        account_id = input("> ")
        if account_id.lower() == "q":
            return None
        if account_id.lower() == "add":
            print("Enter new account name: ")
            account_name = input("> ")
            print("Enter account description (or enter to continue with no description): ")
            account_description = input("> ")
            account = Account(account_name, account_description)
            account_id = account.insert_into_db(database_name)
        
        print("How much of the receipt did you pay with this account?")
        print("Enter payment amount ($): ")
        payment_amount = input("> ")
        if payment_amount.lower() == "q":
            return None
        
        ledger_entries.append([payment_amount, account_id])
        receipt_total -= float(payment_amount)
    return ledger_entries


def _read_expense_transaction_from_user(database_name: str) -> ExpenseTransaction:
    """
    Reads a transaction from the user.

    Arguments:
        database_name: The name of the database to use.

    Returns:
        A Transaction object or None if the user ends input early with 'q' input.

    """
    receipt_user_data = _read_user_receipt()
    if not receipt_user_data:
        return None

    expense_user_data = _read_user_expenses(database_name)
    if not expense_user_data:
        return None

    # Calculate receipt total:
    receipt_total = 0
    for expense in expense_user_data:
        amount = float(expense[1])
        receipt_total += amount
    
    ledger_entries_user_data = _read_user_ledger_entries(database_name, receipt_total)
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

    transaction = ExpenseTransaction(receipt=receipt, expenses=expenses, ledger_entries=ledger_entries)
    return transaction


def _read_user_paystub() -> list:
    """
    Reads all data required from user to initialize a paystub object.

    Returns:
        Either a list of the following:
            paystub_date: The date of the paystub.
            paystub_payer: The payer of the receipt.
        Or None if the user quits early.

    """
    # Get paystub date:
    print("Enter date of receiving the income (YYYY-MM-DD): ")
    paystub_date = input("> ")
    if paystub_date.lower() == "q":
        return None

    # Get receipt location:
    print("Enter payer of the income: ")
    paystub_payer = input("> ")
    if paystub_payer.lower() == "q":
        return None
    return [paystub_date, paystub_payer]


def _read_user_incomes() -> list:
    """
    Reads all data required from user to initialize an income object.

    Specifically, reads in the amount of the income and the details of the income.

    Arguments:
        database_name: The name of the database to use.

    Returns:
        Either a list of the following:
            income_amount: The amount of the income.
            income_details: Any details about the income.
        Or None if the user quits early.

    """
    incomes = []
    while True:
        print("Enter income amount (enter nothing or \"done\" if done entering income events): ")
        income_amount = input("> ")
        if income_amount.lower() == "q":
            return None
        if income_amount == "" or income_amount == "done":
            break
        
        print("Enter income details (or enter to continue with no details): ")
        income_details = input("> ")
        if income_details.lower() == "q":
            return None
        
        incomes.append([income_amount, income_details])
    return incomes


def _read_user_paystub_ledger_entries(database_name: str, paystub_total: float) -> list:
    """
    Reads all data required from user to initialize a paystub_entry object.

    Specifically, reads in the amount of the income and the details of the income.

    Arguments:
        database_name: The name of the database to use.

    Returns:
        Either a list of the following:
            income_amount: The amount of the income.
            income_details: Any details about the income.
        Or None if the user quits early.

    """
    print("What accounts are being credited through this income event?")
    tol = 10e-4
    paystub_entries = []    
    while abs(paystub_total) >= tol:
        print("Remaining: ${:.2f}".format(paystub_total))
        print("Select account receiving money (see accounts below): ")
        print_table(database_name, "accounts")
        print("Enter account id or enter \"add\" to add a new payment type: ")
        account_id = input("> ")
        if account_id.lower() == "q":
            return None
        if account_id.lower() == "add":
            print("Enter new account name: ")
            account_name = input("> ")
            print("Enter account description (or enter to continue with no description): ")
            account_description = input("> ")
            payment_type = Account(account_name, account_description)
            account_id = payment_type.insert_into_db(database_name)
        
        print("How much of the total is being credited to this account?")
        print("Enter credit amount ($): ")
        income_amount = input("> ")
        if income_amount.lower() == "q":
            return None
        
        paystub_entries.append([income_amount, account_id])
        paystub_total -= float(income_amount)
    return paystub_entries


def _read_income_transaction_from_user(database_name: str) -> IncomeTransaction:
    """
    Reads an income transaction from the user.

    Arguments:
        database_name: The name of the database to use.

    Returns:
        An IncomeTransaction object or None if the user ends input early with 'q' input.

    """
    paystub_user_data = _read_user_paystub()
    if not paystub_user_data:
        return None

    income_user_data = _read_user_incomes()
    if not income_user_data:
        return None

    # Calculate paystub total:
    paystub_total = 0
    for income in income_user_data:
        print(income)
        amount = float(income[0])
        paystub_total += amount
    
    paystub_ledger_entries_user_data = _read_user_paystub_ledger_entries(database_name, paystub_total)
    if not paystub_ledger_entries_user_data:
        return None
    
    paystub_date = paystub_user_data[0]
    paystub_payer = paystub_user_data[1]

    paystub = Paystub(total="{:.2f}".format(paystub_total), date=paystub_date, payer=paystub_payer)

    incomes = []
    for inc in income_user_data:
        income_amount = inc[0]
        income_details = inc[1]
        income = Income(amount=income_amount, paystub=paystub, details=income_details)
        incomes.append(income)
    
    paystub_ledger_entries = []
    for paystub_ledger_entry in paystub_ledger_entries_user_data:
        paystub_ledger_amount = paystub_ledger_entry[0]
        paystub_ledger_account_id = paystub_ledger_entry[1]
        paystub_ledger_entry = PaystubLedger(amount=paystub_ledger_amount, paystub=paystub, account_id=paystub_ledger_account_id)
        paystub_ledger_entries.append(paystub_ledger_entry)

    transaction = IncomeTransaction(paystub=paystub, income_events=incomes, ledger_entries=paystub_ledger_entries)
    return transaction
    