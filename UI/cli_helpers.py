from collections import Counter
import datetime
from Transactions.categories import Account, ExpenseCategory
from Transactions.expenses import Expense, LedgerEntry, Receipt
from Transactions.incomes import Income, Paystub, PaystubLedger
from Database.manage_database import print_table, _search_categories, _search_expenses
from prompt_toolkit.completion import FuzzyWordCompleter
from prompt_toolkit.shortcuts import prompt
import os
import re
from Transactions.transactions import IncomeTransaction, ExpenseTransaction



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
    path = "."
    files = []
    for r, _, f in os.walk(path):
        for file in f:
            files.append(os.path.join(r, file))
    matches = list(filter(lambda x: db_regex.match(x), files))
    if len(matches) == 0:
        return ""
    elif len(matches) == 1:
        return matches[0]
    else:
        print("Multiple databases found, please enter the index of the database you want to use: ")
        for i, match in enumerate(matches):
            print(f"{i+1}: {match}")
        try:
            db_idx = int(input("> "))
            assert(db_idx >= 1 and db_idx <= len(matches))
        except ValueError:
            print("Invalid selection.")
            return ""
        except AssertionError:
            print("Invalid selection.")
            return ""
        return matches[db_idx - 1]


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
    
    valid = False
    while not valid:
        try:
            datetime.datetime.strptime(receipt_date, '%Y-%m-%d')
            valid = True
        except ValueError:
            print("Invalid date format. Try again.")
            receipt_date = input("> ")
            if receipt_date.lower() == "q":
                return None
    
    # Get receipt location:
    print("Enter location of expense(s): ")
    receipt_location = input("> ")
    if receipt_location.lower() == "q":
        return None
    return [receipt_date, receipt_location]


def _apply_tax(expense_amount: float) -> float:
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
    return expense_amount


def _read_expense_name(database_name: str) -> str:
    print("Enter expense name (enter nothing or \"done\" if done entering expenses): ")
    expense_names = list(set(_search_expenses(database_name)['item']))
    expense_name_completer = FuzzyWordCompleter(expense_names)
    expense_name = prompt(
        "> ",
        completer=expense_name_completer,
        complete_while_typing=True
    )
    if expense_name.lower() == "q":
        return None
    if expense_name.lower() == "done":
        return "done"
    
    # Enforce that the expense name cannot be empty string
    valid = False
    while not valid:
        if not expense_name:
            print("Expense name cannot be empty.")
            expense_name = prompt(
            "> ",
            completer=expense_name_completer,
            complete_while_typing=True
            )       
            if expense_name.lower() == "q":
                return None
            if expense_name.lower() == "done":
                return "done"
            continue
        valid = True

    return expense_name


def _read_expense_amount(database_name: str, expense_name: str) -> float:
    print("Enter expense amount ($): ")
    # it appears autocompleter requires strings, not float
    expense_amounts = list(str(x) for x in set(_search_expenses(database_name, expense_item=expense_name)['amount']))
    expense_amount_completer = FuzzyWordCompleter(expense_amounts)
    expense_amount = prompt(
        "> ",
        completer=expense_amount_completer,
        complete_while_typing=True
    )
    
    if expense_amount.lower() == "q":
        return None
    if expense_amount.lower() == "done":
        return "done"

    valid = False
    while not valid:
        try:
            expense_amount = float(expense_amount)
            valid = True
        except ValueError:
            print("Invalid amount entered, please try again: ")
            expense_amount = prompt(
            "> ",
            completer=expense_amount_completer,
            complete_while_typing=True
        )          
            if expense_amount.lower() == "q":
                return None
            if expense_amount.lower() == "done":
                return "done"                    
    expense_amount = _apply_tax(expense_amount)
    return float(expense_amount)


def _read_expense_type(database_name: str, expense_name: str) -> str:
    print("Enter type of expense (want, need, or savings): ")

    expense_types = list(set(_search_expenses(database_name, expense_item=expense_name)['type']))
    if expense_types:
        type_counter = Counter(expense_types)
        most_common_type = type_counter.most_common(1)[0][0]
        print(f"You usually enter \033[1m{expense_name}\033[0m with the type \033[1m{most_common_type}\033[0m.")
        print(f"\033[1mPress enter to accept\033[0m this suggestion or enter \'want\', \'need\', or \'savings\' for {expense_name}.")

    all_types = ['want', 'need', 'savings']
    expense_type_completer = FuzzyWordCompleter(all_types)
    expense_type = prompt(
        "> ",
        completer=expense_type_completer,
        complete_while_typing=True
    )

    if expense_type.lower() == "q":
        return None
    if expense_type.lower() == "done":
        return "done"

    # User accepts suggestion
    if expense_types and not expense_type:
        return most_common_type

    while expense_type.lower() not in all_types:
        print("Invalid type entered, please try again: ")
        expense_type = prompt(
            "> ",
            completer=expense_type_completer,
            complete_while_typing=True
        )
        if expense_type.lower() == "q":
            return None
        if expense_type.lower() == "done":
            return "done"

    return expense_type


def _read_expense_category(database_name: str, expense_name: str) -> int:
    print(f"Printing categories...")
    print_table(database_name, "categories")

    expense_categories = list(set(_search_expenses(database_name, expense_item=expense_name)['category_id']))
    all_categories_map = _search_categories(database_name)

    if expense_categories:
        existing_expense_category_map = _search_categories(database_name, expense_categories)

        # Find most common category and subcategory names:
        category_counter = Counter(existing_expense_category_map['category'])
        subcategory_counter = Counter(existing_expense_category_map['subcategory'])
        most_common_category_name = category_counter.most_common(1)[0][0]
        most_common_subcategory_name = subcategory_counter.most_common(1)[0][0]

        if most_common_subcategory_name:
            print(f"You usually enter \033[1m{expense_name}\033[0m with the Category as \033[1m{most_common_category_name}\033[0m and Subcategory as \033[1m{most_common_subcategory_name}\033[0m.")
        else:
            print(f"You usually enter \033[1m{expense_name}\033[0m with the Category as \033[1m{most_common_category_name}\033[0m and no Subcategory.")
        print(f"\033[1mPress enter to accept\033[0m this suggestion or select expense category name or id for {expense_name} from table above.")
    else:
        print("Select a category name or a row id from the table above or enter \"add\" to add a new category: ")
    expense_category_completer = FuzzyWordCompleter(list(set(all_categories_map['category'])))

    expense_category = prompt(
        "> ",
        completer=expense_category_completer,
        complete_while_typing=True
    )
    if expense_category == "q":
        return None
    if expense_category == "done":
        return "done"

    # User accepts suggestion
    if expense_categories and not expense_category:
        expense_category_id = existing_expense_category_map['id'][existing_expense_category_map['category'].index(most_common_category_name)]
        return int(expense_category_id)
    
    valid_choices = list(set(all_categories_map['category'])) + ["q"] + ["add"] + ["done"]
    while not expense_category.strip().isnumeric() and expense_category not in valid_choices:
        print("Invalid entry. Please try again: ")
        expense_category = prompt(
            "> ",
            completer=expense_category_completer,
            complete_while_typing=True
        )
        if expense_category.lower() == "q":
            return None
        if expense_category.lower() == "done":
            return "done"

    if expense_category == "add":
        print("Enter new expense category name: ")
        expense_category_name = input("> ")
        if expense_category_name.lower() == "q":
            return None
        if expense_category_name.lower() == "done":
            return "done"
        print("Enter expense subcategory name (or enter to continue with no subcategory): ")
        expense_subcategory = input("> ")
        if expense_subcategory.lower() == "q":
            return None
        if expense_subcategory.lower() == "done":
            return "done"
        expense_cat = ExpenseCategory(expense_category_name, expense_subcategory)
        expense_category_id = expense_cat.insert_into_db(database_name)
        return int(expense_category_id)

    # User enters row id
    if expense_category.strip().isnumeric():
        expense_category_id = int(expense_category)
        return int(expense_category_id)

    # Else, the user entered a category name so we need to read the subcategory:
    expense_subcategory_completer = FuzzyWordCompleter(list(set(all_categories_map['subcategory'])))
    print("Select a subcategory name from the table above: ")
    expense_subcategory = prompt(
            "> ",
            completer=expense_subcategory_completer,
            complete_while_typing=True
        )
    if expense_subcategory.lower() == "q":
            return None
    if expense_subcategory.lower() == "done":
        return "done"

    # Error handling: if user enters something invalid, continue until they enter a valid subcategory
    valid = False
    while not valid:
        try:
            expense_category_id = all_categories_map['id'][all_categories_map['subcategory'].index(expense_subcategory)]
            valid = True
        except ValueError:
            print("Invalid subcategory name. Please try again: ")
            expense_subcategory = prompt(
                "> ",
                completer=expense_subcategory_completer,
                complete_while_typing=True
            )
            if expense_subcategory.lower() == "q":
                return None
            if expense_subcategory.lower() == "done":
                return "done"
    
    return int(expense_category_id)


def _read_expense_details() -> str:
    print("Enter any details about the expense (or enter to continue with no details): ")
    # Here print most common "details" if previously entered this expense.
    # print("Note: you have entered this with {} in the details before.")
    expense_details = input("> ")
    if expense_details.lower() == "q":
        return None
    if expense_details.lower() == "done":
                return "done"
    return expense_details


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
        expense_name = _read_expense_name(database_name)
        if not expense_name:
            return None
        if expense_name == "done":
            break
        
        expense_amount = _read_expense_amount(database_name, expense_name)
        if not expense_amount:
            return None
        if expense_amount == "done":
            break

        expense_type = _read_expense_type(database_name, expense_name)
        if not expense_amount:
            return None
        if expense_amount == "done":
            break

        expense_category_id = _read_expense_category(database_name, expense_name)
        if not expense_category_id:
            return None
        if expense_category_id == "done":
            break
        
        expense_details = _read_expense_details()
        # Need to check if user returned an empty string or "None". None = user quit early and empty string = user entered nothing
        if not isinstance(expense_details, str) and not expense_details:
            return None
        if expense_details == "done":
            break
        
        expenses.append([expense_name, expense_amount, expense_type, expense_category_id, expense_details])
        print("Expense recorded.")

    return expenses


def _read_user_ledger_entries(database_name: str, receipt_total: float) -> list[list[float, int]]:
    print("How did you pay?")
    tol = 10e-3
    ledger_entries = []
    while abs(receipt_total) >= tol:
        print(receipt_total)
        print(type(receipt_total))
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
        
        print(f"How much of the remaining ${receipt_total:.2f} did you pay with this account?")
        print(f"Enter payment amount ($) or press enter if you paid the remaining ${receipt_total:.2f} with acccount id {account_id}: ")
        payment_amount = input("> ")
        if payment_amount.lower() == "q":
            return None
        if not payment_amount:
            payment_amount = receipt_total
        
        ledger_entries.append([float(payment_amount), int(account_id)])
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
        amount = expense[1]
        receipt_total += amount
    
    ledger_entries_user_data = _read_user_ledger_entries(database_name, receipt_total)
    if not ledger_entries_user_data:
        return None
    
    receipt_date = receipt_user_data[0]
    receipt_location = receipt_user_data[1]
    receipt = Receipt(total=f"{receipt_total:.2f}", date=receipt_date, location=receipt_location)

    expenses = []
    for exp in expense_user_data:
        expense_name = exp[0]
        expense_amount = exp[1]
        expense_type = exp[2]
        expense_category = exp[3]
        expense_details = exp[4]
        expense = Expense(item=expense_name, amount=f"{expense_amount:.2f}", type=expense_type,\
                          details=expense_details, receipt=receipt, category_id=expense_category)
        expenses.append(expense)
    
    ledger_entries = []
    for ledger_entry in ledger_entries_user_data:
        payment_amount = ledger_entry[0]
        account_id = ledger_entry[1]
        # added float typecast to ensure that we get 2 decimal places for now. this is a temporary fix.
        ledger_entry = LedgerEntry(amount=f"{float(payment_amount):.2f}", receipt=receipt, account_id=account_id)
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
    