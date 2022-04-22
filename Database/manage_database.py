from contextlib import contextmanager
from fuzzywuzzy import fuzz
import logging
from prettytable import PrettyTable, from_db_cursor
import sqlite3
from typing import Tuple


# Constants:
SEARCH_THRESHOLD = 70


@contextmanager
def _create_connection(db_file: str):
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
    with _create_connection(database_name) as c:

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


def _insert_into_table(database_name: str, table_name: str, values: list, cols: list = [] )-> int:
    """
    Insert a row into a table in the database.

    Args:
        database_name: The name of the database to insert the row into.
        table_name: The name of the table to insert the row into.
        values: The values to insert into the columns.
        cols: The names of the columns to insert into. Default is the empty list, which means all columns will be inserted.

    Returns:
        The id of the row inserted.
    """
    logging.basicConfig(level=logging.INFO)
    with _create_connection(database_name) as c:

        # Check that the values are not empty
        if len(values) == 0:
            logging.error("No values to insert.")
            return

        # Create the string of column names
        col_str = ", ".join(str(i) for i in cols)
        
        # Create the string of values
        val_str = ", ".join("\'" + str(i) + "\'" for i in values)

        # Insert the row
        if len(col_str) == 0:
            c.execute(f"INSERT INTO {table_name} VALUES ({val_str})")
        else:
            c.execute(f"INSERT INTO {table_name} ({col_str}) VALUES ({val_str})")

        # Retrieve ID of the last row inserted.
        row_id = c.execute(f"""SELECT last_insert_rowid()""").fetchone()[0]
        return row_id


def initialize_empty_db(database_name: str):
    with _create_connection(database_name) as c:

        # Payment types table (stores the names of the payment types eg: Visa, Cash, etc...)
        c.execute("""CREATE TABLE IF NOT EXISTS accounts (
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
            type TEXT NOT NULL CONSTRAINT valid_type CHECK(Type IN ('want', 'need', 'savings')),
            receipt_id INTEGER NOT NULL,
            category_id INTEGER NOT NULL,
            details TEXT,
            FOREIGN KEY(receipt_id) REFERENCES receipts(id),
            FOREIGN KEY (category_id) REFERENCES category(id)
        )""")

        # Receipts table (stores details about a single receipt eg: receipt number, amount, date)
        c.execute("""CREATE TABLE IF NOT EXISTS receipts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
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
            account_id INTEGER NOT NULL,
            FOREIGN KEY (receipt_id) REFERENCES receipts(id),
            FOREIGN KEY (account_id) REFERENCES account(id)
        )""")

        # Income table (stores details about income eg: income from a job, etc...)
        c.execute("""CREATE TABLE IF NOT EXISTS incomes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            paystub_id INTEGER NOT NULL,
            details TEXT,
            FOREIGN KEY (paystub_id) REFERENCES paystubs(id)
        )""")

        # Paystubs table (stores date, source, and receiving payment type of pay 
        # eg: paid $1000 on July 1st to chequing account)
        c.execute("""CREATE TABLE IF NOT EXISTS paystubs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            total REAL NOT NULL,
            date TEXT NOT NULL CONSTRAINT valid_date CHECK(Date IS date(Date,'+0 days')),
            payer TEXT NOT NULL
        )""")

        # paystubs_ledger table (stores pretty much the same thing as the ledger table, but for paystubs)
        c.execute("""CREATE TABLE IF NOT EXISTS paystub_ledger (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            paystub_id INTEGER NOT NULL,
            account_id INTEGER NOT NULL,
            FOREIGN KEY (paystub_id) REFERENCES paystubs(id),
            FOREIGN KEY (account_id) REFERENCES accounts(id)
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
    with _create_connection(database_name) as c:
        try:
            c.execute(sql_query)
        except sqlite3.OperationalError as e:
            logging.error(f"Invalid SQL query. See error message -> {e}")
            return

        return c.fetchall()


def _search_expenses(database_name: str, expense_item: str = "", days: str = 365)-> dict:
    """
    Searches for the expense in the database.

    Args:
        database_name: The name of the database to search.
        expense_item: The item to search for.
        days: How many days to limit the search to.

    Returns:
        A list of the expense names that fit the criteria.
    """
    with _create_connection(database_name) as c:
        if not expense_item:
            c.execute(f"""
            SELECT e.id, item, amount, type, receipt_id, category_id, details  \
                FROM receipts INNER JOIN (SELECT * FROM expenses e1 WHERE NOT EXISTS \
                    (SELECT * FROM expenses e2 WHERE e1.item = e2.item and e2.id < e1.id)) e ON receipts.id = e.receipt_id\
                WHERE JulianDay('now') - JulianDay(date) <= {days}""")
        else:
            c.execute(f"""
            SELECT e.id, item, amount, type, receipt_id, category_id, details\
                FROM receipts INNER JOIN (SELECT * FROM expenses e1 WHERE NOT EXISTS \
                    (SELECT * FROM expenses e2 WHERE e1.item = e2.item and e2.id < e1.id)) e ON receipts.id = e.receipt_id\
                WHERE JulianDay('now') - JulianDay(date) <= {days} AND item = '{expense_item}'""")
        result = {col_data[0]: [] for col_data in c.description}
        for row in c.fetchall():
            for col_index, col_data in enumerate(row):
                result[c.description[col_index][0]].append(col_data)
        # desc = c.description
        # column_names = [col[0] for col in desc]
        # result = [dict(zip(column_names, row))  
        #         for row in c.fetchall()]
        return result


def _search_categories(database_name: str, category_ids: list[int] = []) -> dict:
    """
    Search for a category in the database.

    Args:
        database_name: The name of the database to search in.
        category_id: The category to search for.

    Returns:
        A dictionary of values for the list of category ids. If no list is specified, all categories are returned.
    """
    with _create_connection(database_name) as c:
        if not category_ids:
            c.execute("SELECT * FROM categories")
        else:
            c.execute(f"SELECT * FROM categories WHERE id IN { '(' + str(category_ids)[1:-1] + ')'}")
        result = {col_data[0]: [] for col_data in c.description}
        for row in c.fetchall():
            for col_index, col_data in enumerate(row):
                result[c.description[col_index][0]].append(col_data)
        return result


def delete_row(database_name: str, table_name: str, row_id: int) -> None:
    """
    Delete a row from the database.

    Args:
        database_name: The name of the database to delete from.
    """
    with _create_connection(database_name) as c:
        c.execute(f"DELETE FROM {table_name} WHERE id = '{row_id}'")
