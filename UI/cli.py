from collections import Counter
import cv2
from Database.database import Database
import datetime
import numpy as np
from PIL import Image
from prompt_toolkit.completion import FuzzyCompleter
from prompt_toolkit.shortcuts import prompt
import pytesseract
import sys
from Transactions.categories import Account, ExpenseCategory
from Transactions.expenses import Expense, LedgerEntry, Receipt
from Transactions.incomes import Income, Paystub, PaystubLedger
from Transactions.transactions import IncomeTransaction, ExpenseTransaction
from UI.cli_autocompleter import CustomCompleter
from UI.menu import Menu
from UI.program_menus import IndexMenu, MainMenu, TableMenu


# CONSTANTS
HST_TAX_RATE = 0.13


# HELPERS
def _apply_tax(expense_amount: float) -> float:
    """
    _apply_tax takes a float expense amount and returns the amount after tax, if the expense is taxable.

    Args:
        expense_amount: float, the amount of the expense.

    Returns:
        float, the amount of the expense after tax, if applicable.
    """
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
            valid = False
            while not valid:
                try:
                    tax_rate = float(tax_rate)
                    valid = True
                except ValueError:
                    print("Invalid input. Try again.")
                    tax_rate = input("> ")
                    if tax_rate.lower() == "q":
                        return None
                    if tax_rate == "":
                        tax_rate = HST_TAX_RATE
                        valid = True
        expense_amount = float(expense_amount) * (1 + tax_rate)
        
    return expense_amount


class CLI():
    @staticmethod
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
        return {'date': receipt_date, 'location': receipt_location}

    @staticmethod
    def _read_expense_name(expense_name_completer: FuzzyCompleter) -> str:
        print("Enter expense name (enter nothing or \"done\" if done entering expenses): ")
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

    @staticmethod
    def _read_expense_amount(expense_amount_completer: FuzzyCompleter) -> float:
        print("Enter expense amount ($): ")
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

    @staticmethod
    def _read_expense_type(expense_name: str, expense_types: list, completer: FuzzyCompleter) -> str:
        print("Enter type of expense (want, need, or savings): ")

        expense_types_no_duplicates = list(dict.fromkeys(expense_types))
        if expense_types_no_duplicates:
            type_counter = Counter(expense_types_no_duplicates)
            most_common_type = type_counter.most_common(1)[0][0]
            print(f"You usually enter \033[1m{expense_name}\033[0m with the type \033[1m{most_common_type}\033[0m.")
            print(f"\033[1mPress enter to accept\033[0m this suggestion or enter \'want\', \'need\', or \'savings\' for {expense_name}.")

        all_types = ['want', 'need', 'savings']
        expense_type = prompt(
            "> ",
            completer=completer,
            complete_while_typing=True
        )

        if expense_type.lower() == "q":
            return None
        if expense_type.lower() == "done":
            return "done"

        # User accepts suggestion
        if expense_types_no_duplicates and not expense_type:
            return most_common_type

        while expense_type.lower() not in all_types:
            print("Invalid type entered, please try again: ")
            expense_type = prompt(
                "> ",
                completer=completer,
                complete_while_typing=True
            )
            if expense_type.lower() == "q":
                return None
            if expense_type.lower() == "done":
                return "done"

        return expense_type
        
    @staticmethod
    def _read_expense_category(
        database: Database, 
        expense_name: str, 
        category_map_existing: dict,
        category_map_all: dict
        ) -> int:

        print(f"Printing categories...")
        database.print_table("categories")

        if category_map_existing:

            # Find most common category and subcategory names:
            category_counter = Counter(category_map_existing['category'])
            subcategory_counter = Counter(category_map_existing['subcategory'])
            most_common_category_name = category_counter.most_common(1)[0][0]
            most_common_subcategory_name = subcategory_counter.most_common(1)[0][0]

            if most_common_subcategory_name:
                print(f"You usually enter \033[1m{expense_name}\033[0m with the Category as \033[1m{most_common_category_name}\033[0m and Subcategory as \033[1m{most_common_subcategory_name}\033[0m.")
            else:
                print(f"You usually enter \033[1m{expense_name}\033[0m with the Category as \033[1m{most_common_category_name}\033[0m and no Subcategory.")
            print(f"\033[1mPress enter to accept\033[0m this suggestion or select expense category name or id for {expense_name} from table above.")
        else:
            print("Select a category name or a row id from the table above or enter \"add\" to add a new category: ")

        category_completer = FuzzyCompleter(CustomCompleter(list(dict.fromkeys(category_map_all['category']))))
        expense_category = prompt(
            "> ",
            completer=category_completer,
            complete_while_typing=True
        )
        if expense_category == "q":
            return None
        if expense_category == "done":
            return "done"

        # User accepts suggestion
        if category_map_existing and not expense_category:
            expense_category_id = category_map_existing['id'][category_map_existing['category'].index(most_common_category_name)]
            return int(expense_category_id)
        
        # Verify user entered a valid input
        valid_choices = list(dict.fromkeys(category_map_all['category'])) + ["q"] + ["add"] + ["done"]
        while not expense_category.strip().isnumeric() and expense_category not in valid_choices:
            print("Invalid entry. Please try again: ")
            expense_category = prompt(
                "> ",
                completer=category_completer,
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
            # check if table categories exists and has column category_type
            if "category_type" in category_map_all:
                all_types = ['want', 'need', 'savings']
                print("Enter category type (want, need, or savings): ")
                category_type = input("> ").lower()
                while category_type not in all_types:
                    print("Invalid type entered, please try again: ")
                    category_type = input("> ").lower()
                    if category_type == "q":
                        return None
                    if category_type.lower() == "done":
                        return "done"
            else:
                category_type = None
            expense_cat = ExpenseCategory(expense_category_name, expense_subcategory, category_type)
            expense_category_id = expense_cat.insert_into_db(database)
            return int(expense_category_id)

        # User enters row id
        if expense_category.strip().isnumeric():
            expense_category_id = int(expense_category)
            return int(expense_category_id)

        # Else, the user entered a category name so we need to read the subcategory:
        print("Select a subcategory name from the table above: ")

        # This is pretty unreadable, but it basically finds all potential subcategories that match the category name the user entered.
        subcategory_values = [x for x in category_map_all['subcategory'] if category_map_all['category'][category_map_all['subcategory'].index(x)] == expense_category]
        subcategory_completer = FuzzyCompleter(CustomCompleter(subcategory_values))
        expense_subcategory = prompt(
                "> ",
                completer=subcategory_completer,
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
                expense_category_id = category_map_all['id'][category_map_all['subcategory'].index(expense_subcategory)]
                valid = True
            except ValueError:
                print("Invalid subcategory name. Please try again: ")
                expense_subcategory = prompt(
                    "> ",
                    completer=subcategory_completer,
                    complete_while_typing=True
                )
                if expense_subcategory.lower() == "q":
                    return None
                if expense_subcategory.lower() == "done":
                    return "done"
        
        return int(expense_category_id)
    
    @staticmethod
    def _read_expense_details() -> str:
        print("Enter any details about the expense (or enter to continue with no details): ")
        expense_details = input("> ")
        if expense_details.lower() == "q":
            return None
        if expense_details.lower() == "done":
                    return "done"
        return expense_details

    def _read_user_expenses(self, database: Database) -> list:
        """
        Reads all data required from user to initialize an expense object.

        Specifically, reads in the expense name, amount, type, details, and category id.

        Arguments:
            database_name: The name of the database to use.

        Returns:
            Either a list of the following:
                expense_name: The name of the expense.
                expense_amount: The amount of the expense.
                expense_details: Any details about the expense.
                expense_category_id: The category id of the expense.
            Or None if the user quits early.

        """
        
        expenses = []
        while True:
            user_data = {}
            # Autocompletion for expense names:
            expense_map = database._search_expenses()

            # Read expense name:
            expense_name_completer = FuzzyCompleter(CustomCompleter(expense_map['item']))
            expense_name = self._read_expense_name(expense_name_completer)
            if not expense_name:
                return None
            if expense_name == "done":
                break
            user_data['name'] = expense_name
            
            # Read expense amount:
            expense_map = database._search_expenses(expense_item=expense_name)
            expense_amount_completer = FuzzyCompleter(CustomCompleter(list(str(x) for x in set(expense_map['amount']))))
            expense_amount = self._read_expense_amount(expense_amount_completer)
            if not expense_amount:
                return None
            if expense_amount == "done":
                break
            user_data['amount'] = expense_amount
            
            # Read category id:
            if "category_id" in expense_map.keys():
                categories_map_all = database._search_categories()
                
                # Getting all category ids that have ever been used to categorize the expense:
                expense_category_ids = list(dict.fromkeys(expense_map['category_id']))

                # Need the existing categories for suggestions and need the full categories table for prompt
                # It is probably suboptimal to call _search_categories twice, but this is how it will remain
                # Only do this if there are categories already existing, otherwise _search_categories will be
                # passed an empty list, which results in returning the whole table.
                if expense_category_ids:
                    categories_map_existing = database._search_categories(expense_category_ids)
                else:
                    categories_map_existing = {}

                expense_category_id = self._read_expense_category(
                    database, 
                    expense_name, 
                    categories_map_existing, 
                    categories_map_all)
                if not expense_category_id:
                    return None
                if expense_category_id == "done":
                    break
                user_data['category_id'] = expense_category_id
            
            if "details" in expense_map.keys():
                expense_details = self._read_expense_details()
                # Need to check if user returned an empty string or "None". None = user quit early and empty string = user entered nothing
                if not isinstance(expense_details, str) and not expense_details:
                    return None
                if expense_details == "done":
                    break
                user_data['details'] = expense_details
            
            expenses.append(user_data)
            print("Expense recorded.")

        return expenses

    def _read_user_ledger_entries(self, database: Database, receipt_total: float) -> list[list[float, int]]:
        print("How did you pay?")
        tol = 10e-3
        ledger_entries = []
        while abs(receipt_total) >= tol:
            print("Remaining on receipt: ${:.2f}".format(receipt_total))
            print("Select account id used to pay (see accounts below): ")
            database.print_table("accounts")
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
                account_id = account.insert_into_db(database)
            
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

    def _read_expense_transaction_from_user(self, database: Database) -> ExpenseTransaction:
        """
        Reads a transaction from the user.

        Arguments:
            database_name: The name of the database to use.

        Returns:
            A Transaction object or None if the user ends input early with 'q' input.

        """
        receipt_user_data = self._read_user_receipt()
        if not receipt_user_data:
            return None

        expense_user_data = self._read_user_expenses(database)
        if not expense_user_data:
            return None

        # Calculate receipt total:
        receipt_total = 0
        for expense in expense_user_data:
            amount = expense['amount']
            receipt_total += amount
        
        ledger_entries_user_data = self._read_user_ledger_entries(database, receipt_total)
        if not ledger_entries_user_data:
            return None
        
        receipt_date = receipt_user_data['date']
        receipt_location = receipt_user_data['location']
        receipt = Receipt(total=f"{receipt_total:.2f}", date=receipt_date, location=receipt_location)

        expenses = []
        for exp in expense_user_data:
            expense_name = exp['name']
            expense_amount = exp['amount']
            expense_type = exp.get('type', None)
            expense_category = exp.get('category_id', None)
            expense_details = exp.get('details', None)
            expense = Expense(item=expense_name, amount=f"{expense_amount:.2f}", details=expense_details, \
                             receipt=receipt, category_id=expense_category)
            expenses.append(expense)
        
        ledger_entries = []
        for ledger_entry in ledger_entries_user_data:
            payment_amount = ledger_entry[0]
            account_id = ledger_entry[1]
            ledger_entry = LedgerEntry(amount=f"{float(payment_amount):.2f}", receipt=receipt, account_id=account_id)
            ledger_entries.append(ledger_entry)

        transaction = ExpenseTransaction(receipt=receipt, expenses=expenses, ledger_entries=ledger_entries)
        return transaction

    @staticmethod
    def _read_user_paystub(paystub_payer_completer: FuzzyCompleter) -> dict:
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

        valid = False
        while not valid:
            try:
                datetime.datetime.strptime(paystub_date, '%Y-%m-%d')
                valid = True
            except ValueError:
                print("Invalid date format. Try again.")
                paystub_date = input("> ")
                if paystub_date.lower() == "q":
                    return None

        # Get paystub payer:
        print("Enter the name of the payer: ")
        paystub_payer = prompt(
            "> ",
            completer=paystub_payer_completer,
            complete_while_typing=True
        )
        if paystub_payer.lower() == "q":
            return None
        if paystub_payer.lower() == "done":
            return "done"
        
        # Enforce that the expense name cannot be empty string
        valid = False
        while not valid:
            if not paystub_payer:
                print("Expense name cannot be empty.")
                paystub_payer = prompt(
                "> ",
                completer=paystub_payer_completer,
                complete_while_typing=True
                )       
                if paystub_payer.lower() == "q":
                    return None
                if paystub_payer.lower() == "done":
                    return "done"
                continue
            valid = True
        return {'date': paystub_date, 'payer': paystub_payer}

    @staticmethod
    def _read_user_income_amount(
        income_amount_completer: FuzzyCompleter,
        incomes_existing: dict,
        payer: str
        ) -> float:
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
        if incomes_existing:
            # Find most recent amount in incomes_existing
            # NOTE: we could instead suggest the "most common" amount, but
            #   the downside of this is that if, in the case of a job you
            #   get a promotion, it would take forever for it to change
            #   the most common amount.
            most_recent = incomes_existing['amount'][-1]
            print(f"You last entered an income from \033[1m{payer}\033[0m in the amount of \033[1m${most_recent:.2f}\033[0m.")
            print(f"\033[1mPress enter to accept\033[0m this suggestion or enter a new amount.")
        print("Enter income amount ($): ")
        income_amount = prompt(
        "> ",
        completer=income_amount_completer,
        complete_while_typing=True
        )

        # User accepts suggestion
        if incomes_existing and not income_amount:
            return float(most_recent)
        
        if income_amount.lower() == "q":
            return None
        if income_amount == "" or income_amount == "done":
            return "done"

        valid = False
        while not valid:
            try:
                income_amount = float(income_amount)
                valid = True
            except ValueError:
                print("Invalid amount entered, please try again: ")
                income_amount = prompt(
                "> ",
                completer=income_amount_completer,
                complete_while_typing=True
            )          
                if income_amount.lower() == "q":
                    return None
                if income_amount.lower() == "done":
                    return "done"               
        return float(income_amount)

    @staticmethod
    def _read_user_income_details() -> str:
        print("Enter income details (or enter to continue with no details): ")
        income_details = input("> ")
        if income_details.lower() == "q":
            return None
        if income_details == "done":
            return "done"
        return income_details

    @staticmethod
    def _read_user_paystub_ledger_entries(database: Database, paystub_total: float) -> list:
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
        tol = 10e-3
        paystub_entries = []    
        while abs(paystub_total) >= tol:
            print("Remaining: ${:.2f}".format(paystub_total))
            print("Select account receiving money (see accounts below): ")
            database.print_table("accounts")
            print("Enter account id or enter \"add\" to add a new payment type: ")
            account_id = input("> ")
            if account_id.lower() == "q":
                return None
            if account_id.lower() == "add":
                print("Enter new account name: ")
                account_name = input("> ")
                print("Enter account description (or enter to continue with no description): ")
                account_description = input("> ")
                account = Account(account_name, account_description)
                account_id = account.insert_into_db(database)
            
            print(f"How much of the remaining ${paystub_total:.2f} is being credited to this account?")
            print(f"Enter payment amount ($) or press enter if you received the remaining ${paystub_total:.2f} with acccount id {account_id}: ")

            income_amount = input("> ")
            if income_amount.lower() == "q":
                return None
            if not income_amount:
                income_amount = paystub_total
            
            paystub_entries.append([income_amount, account_id])
            paystub_total -= float(income_amount)
        return paystub_entries

    def _read_user_incomes(self, database: Database, payer: str = "") -> list:
        incomes_existing = database._search_incomes(payer=payer)
        incomes_all = database._search_incomes()

        incomes = []
        # Currently, we only support the case where there's one income per paystub.
        # That'll be fixed later!
        user_data = {}

        # Read income amount
        income_amount_completer = FuzzyCompleter(CustomCompleter(list(str(x) for x in set(incomes_existing['amount']))))
        income_amount = self._read_user_income_amount(income_amount_completer, incomes_existing, payer)

        if not income_amount:
            return None
        user_data['amount'] = income_amount

        # Read income details:
        if "details" in incomes_all.keys():
            income_details = self._read_user_income_details()
            # Need to check if user returned an empty string or "None". None = user quit early and empty string = user entered nothing
            if not isinstance(income_details, str) and not income_details:
                return None
            user_data['details'] = income_details

        incomes.append(user_data)
        
        return incomes

    def _read_income_transaction_from_user(self, database: Database) -> IncomeTransaction:
        """
        Reads an income transaction from the user.

        Arguments:
            database_name: The name of the database to use.

        Returns:
            An IncomeTransaction object or None if the user ends input early with 'q' input.

        """
        existing_payers = database._search_paystubs()
        existing_payers_completer = FuzzyCompleter(CustomCompleter(list(dict.fromkeys(existing_payers['payer']))))

        paystub_user_data = self._read_user_paystub(existing_payers_completer)
        if not paystub_user_data:
            return None

        income_user_data = self._read_user_incomes(database=database, payer=paystub_user_data['payer'])
        if not income_user_data:
            return None
        print(income_user_data)
        # Calculate paystub total:
        paystub_total = 0
        for income in income_user_data:
            amount = float(income['amount'])
            paystub_total += amount
        
        paystub_ledger_entries_user_data = self._read_user_paystub_ledger_entries(database, paystub_total)
        if not paystub_ledger_entries_user_data:
            return None
        
        paystub_date = paystub_user_data['date']
        paystub_payer = paystub_user_data['payer']

        paystub = Paystub(total="{:.2f}".format(paystub_total), date=paystub_date, payer=paystub_payer)

        incomes = []
        for inc in income_user_data:
            income_amount = inc['amount']
            income_details = inc['details']
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

    def run(self, database: Database) -> None:
        # initialize prompt session !!
        main_menu_options = ["Insert expense transaction", "Insert income transaction", "Print table", "Delete row", \
                         "Execute arbitrary sql query", "Scan receipt of expenses", "Exit"]
        main_menu = MainMenu(main_menu_options)
        table_options = database._get_tables()
        table_menu = TableMenu(options=table_options)
        index_menu = IndexMenu(options=table_options)

        while True:
            choice = main_menu.run()
            if choice == 1:
                self.insert_expense_transactions(database)
            elif choice == 2:
                self.insert_income_transactions(database)
            elif choice == 3:
                self.print_table(table_menu, database)
            elif choice == 4:
                self.delete_row(index_menu, database)
            elif choice == 5:
                self.execute_sql_query(database)
            elif choice == 6:
                self.scan_receipt(database)
            elif choice == 7:
                    self.exit()
    
    @staticmethod
    def _initialize_db(db: Database) -> None:
        # Initialize budget database
        print("No database found, creating a new database...")
        print("Enter database name (default name is budget): ")
        database_name = input("> ")

        # If no custome database name is entered, use default name
        if database_name == "":
            database_name = "budget"

        # Adding suffix to database name
        if database_name[-3:] != ".db" or ".sqlite" not in database_name:
            database_name += ".db"

        # Adding path to Database dir
        database_path = "./Database/" + database_name

        # Optional columns:
        excluded_cols = []
        
        # Category table
        print("Would you like to track expense categories? A category table would be created with a category and a subcategory column, as well as a category type which would track if the category is a want, a need, or a savings event. This would allow you to categorize each expense (y/n):")
        category_table = input("> ")
        valid = False
        while not valid:
            if category_table.lower() == "n":
                excluded_cols.append("category_table")
                valid = True
            elif category_table.lower() == "y":
                valid = True
            else:
                print("Invalid input, please enter 'y' or 'n': ")
                category_table = input("> ")
        
        # Category type
        if category_table.lower() == "y":
            print("Would you like to track expense category types? The category table will be created with a category type column, which would track if the category is a want, a need, or a savings event. (y/n):")
            category_type = input("> ")
            valid = False
            while not valid:
                if category_type.lower() == "n":
                    excluded_cols.append("category_type")
                    valid = True
                elif category_type.lower() == "y":
                    valid = True
                else:
                    print("Invalid input, please enter 'y' or 'n': ")
                    category_type = input("> ")
        else:
            excluded_cols.append("category_type")

        # Expense details:
        print("Expense details (ie: when entering expenses, there would be an option to enter any details about the expense (y/n):")
        expense_details = input("> ")
        valid = False
        while not valid:
            if expense_details.lower() == "n":
                excluded_cols.append("details")
                valid = True
            elif expense_details.lower() == "y":
                valid = True
            else:
                print("Invalid input, please enter 'y' or 'n': ")
                expense_details = input("> ")

        # Income details:
        print("Income details (ie: when entering incomes, there would be an option to enter any details about the income (y/n):")
        income_details = input("> ")
        valid = False
        while not valid:
            if income_details.lower() == "n":
                excluded_cols.append("income_details")
                valid = True
            elif income_details.lower() == "y":
                valid = True
            else:
                print("Invalid input, please enter 'y' or 'n': ")
                income_details = input("> ")
        
        # Initialize empty database
        db._create_empty_database(path=database_path, excluded_cols=excluded_cols)

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
            account.insert_into_db(db)

        # Initialize expense categories
        if "category_table" not in excluded_cols:
            print("""Initializing expense categories...
            
The category will be a broad categorization and the subcategory, an optional field, 
will be used to make the category more clear (particularly useful for groceries -- one may 
want to have the category be listed as \'groceries\' and the subcategory be \'chicken\', for example).

The category type is one of "Want", "Need", or "Savings".
            """)

            while True:
                print("Enter category name (eg: grocery, bills, etc...) or q if you are done entering categories: ")
                category_name = input("> ").lower()
                if category_name == "" or category_name.lower() == "q":
                    break
                print("Enter subcategory (can be left blank): ")
                subcategory = input("> ").lower()
                if category_type not in excluded_cols:
                    print("Enter category type (one of want, need, or savings): ")
                    all_expense_types = ["want", "need", "savings"]
                    category_type = input("> ").lower()
                    while category_type not in all_expense_types:
                        print("Invalid input, please enter one of want, need, or savings: ")
                        category_type = input("> ").lower()
                else:
                    category_type = None
                expense_category = ExpenseCategory(category_name, subcategory, category_type)
                expense_category.insert_into_db(db)

    def insert_expense_transactions(self, database_name: str) -> None:
        print("Enter q at any time to stop entering transactions.")
        while True:
            expense_transaction = self._read_expense_transaction_from_user(database_name)
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

    def insert_income_transactions(self, database: Database) -> None:
        print("Enter q at any time to stop entering income transactions.")
        while True:
            income_transaction = self._read_income_transaction_from_user(database)
            if not income_transaction:
                print("Transaction cancelled.")
                break
            else:
                # Insert transaction into database
                retval = income_transaction.execute(database)
                if not retval:
                    print("Income transaction added.")
                else:
                    print(f"Income transaction failed to be added. Error message: {retval}")
    
    @staticmethod
    def print_table(menu: Menu, database: Database) -> None:
        table_name = menu.run()
        database.print_table(table_name)

    @staticmethod
    def delete_row(menu: Menu, database: Database) -> None:
        table_name, row_id = menu.run(database)

        database.delete_row(table_name, row_id)
        print("Row deleted.")
    
    @staticmethod
    def execute_sql_query(database: Database) -> None:
        print("Enter SQL query: ")
        sql_query = input("> ")
        print("Executing query...")
        vals = database.query_db(sql_query)
        print(f"Results: {vals}")

    def scan_receipt(self, database: Database):
        print("Disclaimer: this feature is a work in progress, use at own risk.\nCurrently, only prints receipt text (and the text isn't exactly accurate yet!).")
        print("Enter receipt path: ")
        receipt_path = input("> ")
        print("Scanning receipt...")
        receipt = np.array(Image.open(receipt_path))
        norm_receipt = np.zeros((receipt.shape[0], receipt.shape[1]))
        norm_receipt = cv2.normalize(receipt, norm_receipt, 0, 255, cv2.NORM_MINMAX)
        norm_receipt = cv2.threshold(norm_receipt, 100, 255, cv2.THRESH_BINARY)[1]
        norm_receipt = cv2.GaussianBlur(norm_receipt, (1, 1), 0)
        text = pytesseract.image_to_string(norm_receipt)
        print(text)

    @staticmethod
    def exit() -> None:
        sys.exit(0)
