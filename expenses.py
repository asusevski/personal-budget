from dataclasses import dataclass
#from expense_category import ExpenseCategory
from manage_database import insert_into_table
#from receipt import Receipt


@dataclass
class Expense:
    item: str
    amount: str
    type: str
    #receipt: Receipt
    receipt_id: int
    #category: ExpenseCategory
    category_id: int
    
    def insert_into_db(self, database_name: str) -> int:
        """
        Insert the expense into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            The ID of the expense in the database.

        Effects:
            Modifies table 'expenses' in the database.
        """
        expense_id = insert_into_table(database_name, 'expenses', cols=['item', 'amount', 'type', 'receipt_id', 'category_id'], \
            values=[self.item, self.amount, self.type, self.receipt_id, self.category_id])
        return expense_id
