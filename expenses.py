from dataclasses import dataclass
from expense_category import ExpenseCategory
from receipt import Receipt


@dataclass
class Expense:
    item: str
    amount: str
    type: str
    receipt: Receipt
    category: ExpenseCategory
