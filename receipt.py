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
