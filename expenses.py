#from receipt import Receipt
from expense_category import ExpenseCategoryID
from dataclasses import dataclass

@dataclass
class Expense:
    item: str
    amount: float
    category: ExpenseCategoryID
