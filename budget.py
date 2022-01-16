from modify_database import create_table


def create_expenses(database_name: str) -> None:
    """
    Creates expenses table in the budget.db database.

    The columns of the expense table by default are (ID, Date, Amount, Category, Description)
    where ID is the primary key of the expense table, Date is a YYYY-MM-DD date, Amount is a float,
    Category is an integer corresponding to the category of the expense as defined in the table Categories, 
    and Description is a string.

    Only the columns ID, Date, Amount, Location, Payment ID are required.

    Parameters:
        database_name (str): Name of the database.

    Returns:
        None

    Effects:
        Creates a table in the database.
    """
    cols = {"ID": "INTEGER", "Date": "TEXT", "Amount": "REAL", "Location": "TEXT", "Payment_ID": "INTEGER", "Category": "INTEGER", "Description": "TEXT"}
    constraints = {"ID": "PRIMARY KEY AUTOINCREMENT", "Date": "NOT NULL CONSTRAINT valid_date CHECK(Date IS date(Date,'+0 days'))", \
        "Amount": "NOT NULL", "Location": "NOT NULL", "Payment_ID": "NOT NULL"}
    create_table(database_name, "expenses", cols, constraints)


def create_categories(database_name: str) -> None:
    """
    Creates categories table in budget.db database.

    The columns are (ID, Subcategory, Category). ID is the primary key, Subcategory is a specific classification 
    of the item, and "Category" is the general category, if applicable.

    For example, if inputting a bag of apples that were purchased, the Subcategory would be listed as Fruit, and 
    the Category would be Groceries.

    Only the columns ID and Subcategory are required.

    Parameters:
        database_name (str): Name of the database.

    Returns:
        None

    Effects:
        Creates a table in the database.
    """
    cols = {"ID": "INTEGER", "Subcategory": "TEXT", "Category": "TEXT"}
    constraints = {"ID": "PRIMARY KEY AUTOINCREMENT", "Subcategory": "NOT NULL", "Category": "NOT NULL"}
    create_table(database_name, "categories", cols, constraints)


def create_payment(database_name: str) -> None:
    """
    Creates payment table in budget.db database.

    The columns are (ID, Payment_name). ID is the primary key and Payment_name is the name of the payment method.
    For example, if a payment was made with a Visa ending in 1111, the Payment_name could be "Visa 1111"".

    Both ID and Payment_name are required.

    Parameters:
        database_name (str): Name of the database.

    Returns:
        None

    Effects:
        Creates a table in the database.
    """
    cols = {"ID": "INTEGER", "Payment_name": "TEXT"}
    constraints = {"ID": "PRIMARY KEY AUTOINCREMENT", "Payment_name": "NOT NULL"}
    create_table(database_name, "payment_types", cols, constraints)
