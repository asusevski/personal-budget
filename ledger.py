from dataclasses import dataclass
from manage_database import insert_into_table
from receipt import Receipt
from payment_type import PaymentType


@dataclass
class LedgerEntry():
    """
    This class stores the information about a single transaction in the ledger.
    
    Attributes:
        date: The date of the transaction (YYYY-MM-DD)
        receipt: The receipt associated with the transaction
        payment_type: The payment type associated with the transaction
    """
    amount: str
    receipt: Receipt
    payment_type: PaymentType

    def insert_into_db(self, database_name: str) -> None:
        """
        Insert the receipt into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            None

        Effects:
            Modifies table 'receipts' in the database.
        """
        insert_into_table(database_name, 'receipts', cols=['amount', 'receipt_id', 'payment_type'],\
            values=[self.amount, self.receipt.id, self.payment_type.id])
