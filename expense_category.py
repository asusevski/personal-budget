from dataclasses import dataclass


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
