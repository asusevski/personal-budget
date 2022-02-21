from dataclasses import dataclass
from manage_database import insert_into_table


@dataclass
class ExpenseCategory():
    """
    This class stores the category and subcategory of an expense.

    
    Attributes:
        category: The category of the expense (eg 'Food', 'Transportation', etc.)
        subcategory: The subcategory of the expense (eg  'chicken', 'uber', 'taxi', etc.)
                     This is optional and can be left blank if the category is sufficient to describe the expense.
    """
    id: int
    category: str
    subcategory: str

    def insert_into_db(self, database_name: str):
        """
        Inserts the expense category into the database.
        """
        insert_into_table(database_name, 'categories', values=[self.id, self.category, self.subcategory])
