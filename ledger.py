from dataclasses import dataclass
from manage_database import insert_into_table
#from receipt import Receipt
#from payment_type import PaymentType


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
    #receipt: Receipt
    receipt_id: int
    #payment_type: PaymentType
    payment_type_id: int

    def insert_into_db(self, database_name: str) -> int:
        """
        Insert the receipt into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            The ID of the ledger entry in the database.

        Effects:
            Modifies table 'ledger' in the database.
        """
        ledger_id = insert_into_table(database_name, 'ledger', cols=['amount', 'receipt_id', 'payment_type_id'],\
            values=[self.amount, self.receipt_id, self.payment_type_id])
        return ledger_id
