from dataclasses import dataclass
from expenses import Expense
from ledger import LedgerEntry
from receipt import Receipt
import sqlite3
from manage_database import create_connection


@dataclass
class Transaction:
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

    def execute(self, database_name: str) -> None:
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
        with create_connection(database_name) as c:
            c.execute("begin")
            try:
                receipt_cols = ", ".join(str(i) for i in list(self.receipt.__dict__.keys()))
                receipt_vals = ", ".join("\'" + str(i) + "\'" for i in list(self.receipt.__dict__.values()))

                c.execute(f"""INSERT INTO receipts ({receipt_cols}) VALUES ({receipt_vals})""")

                receipt_id = c.execute(f"""SELECT last_insert_rowid()""").fetchone()[0]
                for expense in self.expenses:
                    expense_cols = ", ".join(str(i) for i in list(expense.__dict__.keys()))
                    expense_vals = list(expense.__dict__.values())
                    expense_vals = expense_vals[:4] + [receipt_id] + expense_vals[5]
                    expense_vals = ", ".join("\'" + str(i) + "\'" for i in expense_vals)

                    c.execute(f"""INSERT INTO expenses ({expense_cols}) VALUES ({expense_vals})""")
                for ledger_entry in self.ledger_entries:
                    ledger_cols = ", ".join(str(i) for i in list(ledger_entry.__dict__.keys()))
                    ledger_vals = list(ledger_entry.__dict__.values())
                    ledger_vals = ledger_vals[0] + [receipt_id] + ledger_vals[1]
                    ledger_vals = ", ".join("\'" + str(i) + "\'" for i in ledger_vals)
                    c.execute(f"""INSERT INTO ledger ({ledger_cols}) VALUES ({ledger_vals})""")

                c.execute("commit")
            except sqlite3.OperationalError as e:
                c.execute("rollback")
                