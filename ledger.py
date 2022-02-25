from dataclasses import dataclass
#from manage_database import insert_into_table
from receipt import Receipt


@dataclass
class LedgerEntry():
    """
    This class stores the information about a single transaction in the ledger.
    
    Attributes:
        date: The date of the transaction (YYYY-MM-DD)
        receipt: The receipt associated with the transaction
        payment_type: The payment type associated with the transaction

    Methods:
        insert_into_db(self, database_name): Insert the ledger entry into the database.

    """
    amount: str
    receipt: Receipt
    payment_type_id: int
    