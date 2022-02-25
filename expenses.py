from dataclasses import dataclass
from expense_category import ExpenseCategory
from manage_database import insert_into_table
from receipt import Receipt


@dataclass
class Expense:
    """
    This class stores the details about a single expense.
    
    Attributes:
        item: The name of the expense
        amount: The price of the expense
        type: The type of the expense (eg: 'want', 'need', 'savings')
        receipt_id: The id of the receipt associated with the expense assigned by the database.
        category_id: The id of the expense category associated with the expense assigned by the database.
        
    """
    item: str
    amount: str
    type: str
    details: str
    receipt: Receipt
    category_id: int
    
