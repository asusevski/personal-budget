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

    def insert_into_db(self, database_name: str):
        """
        Inserts the ledger entry into the database.
        """
        insert_into_table(database_name, 'ledger', values=[self.date, self.receipt.id, self.payment_type.id],
                                                   cols=['amount', 'receipt_id', 'payment_type_id'])
