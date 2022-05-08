from dataclasses import dataclass
from Database.database import Database
#from Database.manage_database import _insert_into_table


@dataclass
class Paystub:
    """
    This class stores the details about a paystub.
    
    Attributes:
        total: The total income of the paystub.
        date: The date of the receipt (YYYY-MM-DD)
        payer: The source of the paystub (eg: 'work')

    Methods:
        insert_into_db(self, database_name): Insert the receipt into the database.
        
    """
    total: float
    date: str
    payer: str

    def insert_into_db(self, database: Database) -> int:
        """
        Insert the receipt into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            The ID of the receipt in the database.

        Effects:
            Modifies table 'receipts' in the database.
        """
        paystub_id = database._insert_into_table('paystub', cols=['total', 'date', 'payer'], \
                          values=[self.total, self.date, self.payer])
        return paystub_id


@dataclass
class Income:
    """
    This class stores the details about a single income instance. 
    """
    amount: str
    paystub: Paystub
    details: str = None


@dataclass
class PaystubLedger():
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
    paystub: Paystub
    account_id: int
