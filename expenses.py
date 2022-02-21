from dataclasses import dataclass
from expense_category import ExpenseCategory
from manage_database import insert_into_table
from receipt import Receipt


@dataclass
class Expense:
    item: str
    amount: str
    type: str
    receipt: Receipt
    category: ExpenseCategory

    def insert_into_db(self, database_name: str):
        """
        Inserts the expense into the database.
        """
        insert_into_table(database_name, 'expenses', cols=['item','amount', 'type', 'receipt_id', 'item_category_id'],
                          values=[self.item, self.amount, self.type, self.receipt.id, self.category.id])
