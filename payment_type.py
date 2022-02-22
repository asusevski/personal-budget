from dataclasses import dataclass
from manage_database import insert_into_table


@dataclass
class PaymentType:
    id: int
    name: str
    description: str

    def insert_into_db(self, database_name: str) -> None:
        """
        Insert the payment type into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            None

        Effects:
            Modifies table 'payment_types' in the database.
        """
        insert_into_table(database_name, 'payment_types', values=[self.id, self.name, self.description])

