from enum import Enum, auto

class ExpenseCategoryID(Enum):
    food = auto()
    travel = auto()
    entertainment = auto()
    shopping = auto()
    utilities = auto()
    other = auto()

class ExpenseSubcategoryID(Enum):
    meat = auto()
