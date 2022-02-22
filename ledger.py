from dataclasses import dataclass
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
