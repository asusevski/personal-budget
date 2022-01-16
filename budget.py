from modify_database import create_table

def create_expenses(database_name: str) -> None:
    """
    Creates expenses table in the budget.db database.

    The columns of the expense table by default are (ID, Date, Amount, Category, Description)
    where ID is the primary key of the expense table, Date is a YYYY-MM-DD date, Amount is a float,
    Category is an integer corresponding to the category of the expense as defined in the table Categories, 
    and Description is a string.

    Only the columns ID, Date, and Amount are required.

    Parameters:
        database_name (str): Name of the database.

    Returns:
        None

    Effects:
        Creates a table in the database.
    """
    cols = {"ID": "INTEGER", "Date": "TEXT", "Amount": "REAL", "Category": "INTEGER", "Description": "TEXT"}
    constraints = {"ID": "PRIMARY KEY AUTOINCREMENT", "Date": "NOT NULL", "amount": "NOT NULL"}
    create_table(database_name, "expenses", cols, constraints)
