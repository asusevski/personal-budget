from contextlib import contextmanager
from expenses import Expense
from expense_category import ExpenseCategory
from ledger import LedgerEntry
import logging
from payment_type import PaymentType
from prettytable import from_db_cursor
from receipt import Receipt
import sqlite3


@contextmanager
def create_connection(db_file: str):
    """
    Create a database connection to a SQLite database.

    Args:
        db_file: The database file to connect to.

    Yields:
        The database connection.
    """
    conn = sqlite3.connect(db_file)
    try:
        cursor =  conn.cursor()
        yield cursor
    finally:
        logging.info("Closing connection to database.")
        conn.commit()
        conn.close()


def print_table(database_name: str, table_name: str, sql_query: str = "", cols: str = "") -> None:
    """
    Print the contents of a table in the database using package PrettyTable.
    By default, prints the entire table, but can be modified to print a subset of the table.

    Args:
        database_name: The name of the database to print the table from.
        table_name: The name of the table to print.
        sql_query: The SQL query to use to print the table (default is none, which prints the entire table).
        cols: The names of the columns to print (default is none, which prints all columns).
    """
    with create_connection(database_name) as c:

        if sql_query != "":
            try:
                c.execute(sql_query)
            except sqlite3.OperationalError as e:
                logging.error(f"Invalid SQL query. See error message -> {e}")
                return

        elif cols != "":
            try:
                c.execute(f"SELECT {cols} FROM {table_name}")
            except sqlite3.OperationalError as e:
                # Two possible errors: either table name was invalid or column name was invalid
                if "no such table" in str(e):
                    logging.error(f"Table {table_name} does not exist in database {database_name}.")
                    return
                else:
                    # Find the column name(s) in the error message (typical error message has two colons in it, 
                    # the latter of which is directly before the column name that caused an error.
                    logging.error(f"Column {str(e).split(': ')[-1]} does not exist in table {table_name}.")
                    return

        else:
            try:
                c.execute(f"SELECT * FROM {table_name}")
            except:
                logging.error(f"Table {table_name} does not exist.")
                return

        mytable = from_db_cursor(c)
        print(mytable)


def insert_into_table(database_name: str, table_name: str, values: list, cols: list = [] )-> None:
    """
    Insert a row into a table in the database.

    Args:
        database_name: The name of the database to insert the row into.
        table_name: The name of the table to insert the row into.
        values: The values to insert into the columns.
        cols: The names of the columns to insert into. Default is the empty list, which means all columns will be inserted.
    """
    logging.basicConfig(level=logging.INFO)
    with create_connection(database_name) as c:

        # Check that the values are not empty
        if len(values) == 0:
            logging.error("No values to insert.")
            return

        # Create the string of column names
        col_str = ""
        for col in cols:
            col_str += f"{col}, "
        col_str = col_str[:-2]

        # Create the string of values
        val_str = ""
        for val in values:
            if val == "":
                val_str += f"NULL, "
            else:
                val_str += f"'{val}', "
        val_str = val_str[:-2]

        print(val_str)
        # Insert the row
        if len(col_str) == 0:
            c.execute(f"INSERT INTO {table_name} VALUES ({val_str})")
        else:
            c.execute(f"INSERT INTO {table_name} ({col_str}) VALUES ({val_str})")


def initialize_empty_db(database_name: str):
    with create_connection(database_name) as c:

        # Payment types table (stores the names of the payment types eg: Visa, Cash, etc...)
        c.execute("""CREATE TABLE IF NOT EXISTS payment_types (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT
        )""")

        # Categories table (stores category and subcategory of an expense, eg: groceries, rent, etc...)
        c.execute("""CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY,
            category TEXT NOT NULL,
            subcategory TEXT
        )""")

        # Expenses table (stores details about a single expense eg: details on each item of a receipt)
        c.execute("""CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item TEXT NOT NULL,
            amount REAL NOT NULL,
            location TEXT NOT NULL,
            type TEXT NOT NULL CONSTRAINT valid_type CHECK(Type IN ('want', 'need', 'savings')),
            receipt_id INTEGER NOT NULL,
            item_category_id INTEGER NOT NULL,
            FOREIGN KEY(receipt_id) REFERENCES receipts(id),
            FOREIGN KEY (item_category_id) REFERENCES category(id)
        )""")

        # Receipts table (stores details about a single receipt eg: receipt number, amount, date)
        c.execute("""CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY,
            amount REAL NOT NULL,
            date TEXT NOT NULL CONSTRAINT valid_date CHECK(Date IS date(Date,'+0 days')),
            location TEXT NOT NULL
        )""")

        # Ledger table (stores details about a payment made with reference to a receipt 
        # eg: given a grocery receipt -- id = 1, this table stores how that total bill was paid, 
        # perhaps with multiple cards. If a payment was made with multiple cards, there will be multiple entries)
        c.execute("""CREATE TABLE IF NOT EXISTS ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            receipt_id INTEGER NOT NULL,
            payment_type_id INTEGER NOT NULL,
            FOREIGN KEY (receipt_id) REFERENCES receipts(id),
            FOREIGN KEY (payment_type_id) REFERENCES payment_types(id)
        )""")


def query_db(database_name: str, sql_query: str) -> list:
    """
    Query the database and return the results.

    Args:
        database_name: The name of the database to query.
        sql_query: The SQL query to use to query the database.

    Returns:
        A list of the results of the query.
    """
    with create_connection(database_name) as c:
        try:
            c.execute(sql_query)
        except sqlite3.OperationalError as e:
            logging.error(f"Invalid SQL query. See error message -> {e}")
            return

        return c.fetchall()


def is_table_empty(database_name: str, table_name: str) -> bool:
    """
    Check if a table in the database is empty.

    Args:
        database_name: The name of the database to query.
        table_name: The name of the table to check.

    Returns:
        True if the table is empty, False otherwise.
    """
    row = query_db(database_name, f"SELECT * FROM {table_name} limit 1")
    return len(row) == 0


def insert_obj_into_db(database_name: str, obj: object) -> None:
    """
    Insert an object into the database.

    Args:
        database_name: The name of the database to insert the object into.
        obj: The object to insert into the database.
    """
    with create_connection(database_name) as c:
        if isinstance(obj, PaymentType):
            insert_into_table(database_name, 'payment_types', values=[obj.id, obj.name, obj.description])

        elif isinstance(obj, ExpenseCategory):
            insert_into_table(database_name, 'categories', values=[obj.id, obj.category, obj.subcategory])

        elif isinstance(obj, Expense):
            insert_into_table(database_name, 'expenses', cols=['item','amount', 'type', 'receipt_id', 'item_category_id'],\
                              values=[obj.item, obj.amount, obj.type, obj.receipt.id, obj.category.id])
        
        elif isinstance(obj, Receipt):
            insert_into_table(database_name, 'receipts', values=[obj.id, obj.total, obj.date, obj.location])

        elif isinstance(obj, LedgerEntry):
            insert_into_table(database_name, 'ledger', values=[obj.date, obj.receipt.id, obj.payment_type.id], \
                              cols=['amount', 'receipt_id', 'payment_type_id'])
        
        else:
            logging.error(f"Invalid object type {type(obj)}")
