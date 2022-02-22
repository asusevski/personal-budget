from dataclasses import dataclass
from manage_database import insert_into_table


@dataclass
class Receipt:
    id: int
    total: float
    date: str
    location: str

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
        insert_into_table(database_name, 'receipts', cols=['total', 'date', 'location'], \
                          values=[self.id, self.total, self.date, self.location])
        