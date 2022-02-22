from dataclasses import dataclass
from expenses import Expense
from ledger import LedgerEntry
from receipt import Receipt


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
    """
    receipt: Receipt
    expenses: list[Expense]
    ledger_entries: list[LedgerEntry]

    def execute(self, database_name: str, receipt: Receipt, expenses: list[Expense], ledger_entries: list[LedgerEntry]) -> None:
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
        return
        #with