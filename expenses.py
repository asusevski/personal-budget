from dataclasses import dataclass
from manage_database import insert_into_table


@dataclass
class Receipt:
    """
    This class stores the details about a receipt.
    
    Attributes:
        total: The total price of the receipt.
        date: The date of the receipt (YYYY-MM-DD)
        location: The location of the receipt (eg: 'Costco')

    Methods:
        insert_into_db(self, database_name): Insert the receipt into the database.
        
    """
    total: float
    date: str
    location: str

    def insert_into_db(self, database_name: str) -> int:
        """
        Insert the receipt into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            The ID of the receipt in the database.

        Effects:
            Modifies table 'receipts' in the database.
        """
        receipt_id = insert_into_table(database_name, 'receipts', cols=['total', 'date', 'location'], \
                          values=[self.total, self.date, self.location])
        return receipt_id


@dataclass
class Expense:
    """
    This class stores the details about a single expense.
    
    Attributes:
        item: The name of the expense
        amount: The price of the expense
        type: The type of the expense (eg: 'want', 'need', 'savings')
        details: Any additional details about the expense
        receipt_id: The id of the receipt associated with the expense assigned by the database.
        category_id: The id of the expense category associated with the expense assigned by the database.
        
    """
    item: str
    amount: str
    type: str
    details: str
    receipt: Receipt
    category_id: int


@dataclass
class LedgerEntry():
    """
    This class stores the information about a single transaction in the ledger.
    
    Attributes:
        date: The date of the transaction (YYYY-MM-DD)
        receipt: The receipt associated with the transaction
        account_id: The account id associated with the transaction

    Methods:
        insert_into_db(self, database_name): Insert the ledger entry into the database.

    """
    amount: str
    receipt: Receipt
    account_id: int
