from dataclasses import dataclass
from manage_database import insert_into_table


@dataclass
class PaymentType:
    #id: int
    name: str
    description: str

    def insert_into_db(self, database_name: str) -> int:
        """
        Insert the payment type into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            The ID of the PaymentType in the database.

        Effects:
            Modifies table 'payment_types' in the database.
        """
        payment_type_id = insert_into_table(database_name, 'payment_types', cols=['name', 'description'],\
                                            values=[self.name, self.description])
        return payment_type_id

