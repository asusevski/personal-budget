from dataclasses import dataclass
from manage_database import insert_into_table


@dataclass
class PaymentType:
    id: int
    name: str
    description: str

    def insert_into_db(self, database_name: str):
        """
        Inserts the payment type into the database.
        """
        insert_into_table(database_name, 'payment_types', values=[self.id, self.name, self.description])
