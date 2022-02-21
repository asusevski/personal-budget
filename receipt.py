from dataclasses import dataclass
from manage_database import insert_into_table


@dataclass
class Receipt:
    id: int
    total: float
    date: str
    location: str

    def insert_into_db(self, database_name: str):
        """
        Inserts the receipt into the database.
        """
        insert_into_table(database_name, 'receipts', values=[self.id, self.total, self.date, self.location])
        