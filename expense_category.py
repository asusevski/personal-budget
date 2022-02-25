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

    Methods:
        insert_into_db(self, database_name): Insert the expense category into the database.
        
    """
    category: str
    subcategory: str

    def insert_into_db(self, database_name: str) -> int:
        """
        Insert the expense category into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            The ID of the expense category in the database.

        Effects:
            Modifies table 'categories' in the database.
        """
        expense_category_id = insert_into_table(database_name, 'categories', cols=['category', 'subcategory'], \
            values=[self.category, self.subcategory])
        return expense_category_id
