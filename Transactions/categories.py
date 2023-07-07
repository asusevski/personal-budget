from dataclasses import dataclass
from Database.database import Database


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
    category_type: str

    def insert_into_db(self, database: Database) -> int:
        """
        Insert the expense category into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            The ID of the expense category in the database.

        Effects:
            Modifies table 'categories' in the database.
        """
        if not self.category_type:
            expense_category_id = database._insert_into_table('categories', cols=['category', 'subcategory'], \
                values=[self.category, self.subcategory])
        else:
            expense_category_id = database._insert_into_table('categories', cols=['category', 'subcategory', 'category_type'], \
                values=[self.category, self.subcategory, self.category_type])
        return expense_category_id


@dataclass
class Account:
    """
    This class stores Accounts. An account object will contain a name and a description.

    eg: name = 'VisaXXXX' and Description = "TD Credit Card"
    
    Attributes:
        name: The name of the payment type (eg 'Mastercard')
        description: A description of the expense (eg 'Costco Credit Card')

    Methods:
        insert_into_db(self, database_name): Insert the payment type into the database.

    """
    name: str
    description: str

    def insert_into_db(self, database: Database) -> int:
        """
        Insert the payment type into the database.

        Args:
            database_name: The name of the database to insert the payment type into.

        Returns:
            The ID of the PaymentType in the database.

        Effects:
            Modifies table 'payment_types' in the database.
        """
        account_id = database._insert_into_table('accounts', cols=['name', 'description'],\
                                            values=[self.name, self.description])
        return account_id
