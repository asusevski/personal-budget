from abc import ABC, abstractmethod
from dataclasses import dataclass
from Database.database import Database
from Transactions.expenses import Expense, LedgerEntry, Receipt
#from Database.manage_database import _create_connection
from Transactions.incomes import Income, Paystub, PaystubLedger
import sqlite3


class Transaction(ABC):
    @abstractmethod
    def execute(self, database_name: str) -> str:
        pass


@dataclass
class ExpenseTransaction(Transaction):
    """
    A transaction in the context of this program is comprised of one receipt, one or more expenses, 
    and one or more ledger entries. A transaction being comprised of one or more expenses reflects 
    that in a single "transaction", there can be multiple items (eg: at the grocery store, one
    can purchase a bag of apples, a bag of apples AND a bag of bananas, etc...). 
    
    The significance of a transaction being comprised of one or more ledger entries reflects that 
    one receipt can be paid across multiple payment sources (imagine a grocery bill being paid
    across multiple credit cards and/or gift cards).

    Attributes:
        receipt: The receipt associated with the transaction
        expenses: The expenses associated with the transaction (all linked to the same receipt)
        ledger_entries: The ledger entries associated with the transaction (all linked to the same receipt)
    """
    receipt: Receipt
    expenses: list[Expense]
    ledger_entries: list[LedgerEntry]

    def execute(self, database: Database) -> None:
        """
        Updates the database with the information about a transaction.

        Args:
            database_name: The name of the database to insert the payment type into.
            receipt: The receipt associated with the transaction
            expenses: The expenses associated with the transaction
            ledger_entries: The ledger entries associated with the transaction

        Returns:
            None

        Effects:
            Modifies table 'receipts', 'ledger' and 'expenses' in the database.
        """
        with database._create_connection() as c:
            c.execute("begin")
            try:
                # Inserting receipt
                receipt_cols = ", ".join(str(i) for i in list(self.receipt.__dict__.keys()))
                receipt_vals = ", ".join("\'" + str(i) + "\'" for i in list(self.receipt.__dict__.values()))
                c.execute(f"""INSERT INTO receipts ({receipt_cols}) VALUES ({receipt_vals})""")

                # Inserting expenses:
                # Getting receipt id for the inserted receipt
                receipt_id = c.execute(f"""SELECT last_insert_rowid()""").fetchone()[0]
                # Inserting expenses
                for expense in self.expenses:
                    expense_cols = [col for col in expense.__dict__.keys() if expense.__dict__[col] is not None]
                    expense_cols_str = ", ".join(str(i) if i != "receipt" else "receipt_id" for i in expense_cols)
                    expense_vals = [val for val in expense.__dict__.values() if val is not None]
                    expense_vals_str = ", ".join("\'" + str(val) + "\'" if not isinstance(val, Receipt) else str(receipt_id) for val in expense_vals )
                    c.execute(f"""INSERT INTO expenses ({expense_cols_str}) VALUES ({expense_vals_str})""")

                # Inserting ledger entries
                for ledger_entry in self.ledger_entries:
                    ledger_cols = [col for col in ledger_entry.__dict__.keys() if ledger_entry.__dict__[col] is not None]
                    ledger_cols_str = ", ".join(str(i) if i != "receipt" else "receipt_id" for i in ledger_cols)
                    ledger_vals = [val for val in ledger_entry.__dict__.values() if val is not None]
                    ledger_vals_str = ", ".join("\'" + str(val) + "\'" if not isinstance(val, Receipt) else str(receipt_id) for val in ledger_vals )
                    c.execute(f"""INSERT INTO ledger ({ledger_cols_str}) VALUES ({ledger_vals_str})""")

                c.execute("commit")
            except sqlite3.OperationalError as e:
                print(e)
                c.execute("rollback")
                return e


@dataclass
class IncomeTransaction(Transaction):
    """
    An income transaction is a transaction that is comprised of one paystub, one or more income events, 
    and one or more ledger entries. Note that by far, there will almost always be one income event and
    one ledger entry. However, it was important to leave room for an income event to be split up across
    multiple accounts (for example, imagine one purchases an item at a store and paid across two 
    accounts -- if a refund is made, the refund should be split across the same two accounts). Of
    course, one can also just delete the expense and not have to worry about adding an income event for
    the refund, but we leave such details to the user.

    We also leave room for an income event to be split across multuple "income events"; an example where that
    would be useful is if a paycheck is paid in different parts (consider a waiter who may get $100 from tips
    and $200 from salary, and the paycheck total would be $300).
    
    As of May 16th, 2020, we are not implementing this feature (there must be one income event per paystub for now).

    Attributes:
        paystub: The paystub associated with the transaction
        income_events: The income events associated with the transaction (all linked to the same paystub)
        ledger_entries: The ledger entries associated with the transaction (all linked to the same paystub)
    """
    paystub: Paystub
    income_events: list[Income]
    ledger_entries: list[PaystubLedger]

    def execute(self, database: Database) -> None:
        """
        Updates the database with the information about a transaction.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            None

        Effects:
            Modifies table 'paystubs', 'paystub_ledger' and 'incomes' in the database.
        """
        with database._create_connection() as c:
            c.execute("begin")
            try:
                paystub_cols = ", ".join(str(i) for i in list(self.paystub.__dict__.keys()))
                paystub_vals = ", ".join("\'" + str(i) + "\'" for i in list(self.paystub.__dict__.values()))

                c.execute(f"""INSERT INTO paystubs ({paystub_cols}) VALUES ({paystub_vals})""")

                paystub_id = c.execute(f"""SELECT last_insert_rowid()""").fetchone()[0]
                for income in self.income_events:
                    income_cols = list(income.__dict__.keys())
                    income_cols = ", ".join(str(i) if i != "paystub" else "paystub_id" for i in income_cols)
                    income_vals = list(income.__dict__.values())
                    income_vals = [income_vals[0]] + [paystub_id] + [income_vals[2]]
                    income_vals = ", ".join("\'" + str(i) + "\'" for i in income_vals)

                    c.execute(f"""INSERT INTO incomes ({income_cols}) VALUES ({income_vals})""")
                for ledger_entry in self.ledger_entries:
                    ledger_cols = list(ledger_entry.__dict__.keys())
                    ledger_cols = ", ".join(str(i) if i != "paystub" else "paystub_id" for i in ledger_cols)
                    ledger_vals = list(ledger_entry.__dict__.values())
                    ledger_vals = [ledger_vals[0]] + [paystub_id] + [ledger_vals[2]]
                    ledger_vals = ", ".join("\'" + str(i) + "\'" for i in ledger_vals)
                    c.execute(f"""INSERT INTO paystub_ledger ({ledger_cols}) VALUES ({ledger_vals})""")

                c.execute("commit")
            except sqlite3.OperationalError as e:
                c.execute("rollback")
                return e
