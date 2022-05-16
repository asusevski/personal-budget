from contextlib import contextmanager
from dataclasses import dataclass
import logging
import os
from prettytable import from_db_cursor
import re
import sqlite3


@dataclass
class Database:
    def __init__(self):
        db_regex = re.compile(r'(.*)(\.db|\.sqlite3)$')
        path = "."
        files = []
        for r, _, f in os.walk(path):
            for file in f:
                files.append(os.path.join(r, file))
        matches = list(filter(lambda x: db_regex.match(x), files))
        if len(matches) == 0:
            self.path = None
        elif len(matches) == 1:
            self.path = matches[0]
        else:
            print("Multiple databases found, please enter the index of the database you want to use: ")
            for i, match in enumerate(matches):
                print(f"{i+1}: {match}")
            try:
                db_idx = int(input("> "))
                assert(db_idx >= 1 and db_idx <= len(matches))
            except ValueError:
                print("Invalid selection.")
                self.path = None
            except AssertionError:
                print("Invalid selection.")
                self.path = None
            self.path = matches[db_idx - 1]
            self.history = []

    @contextmanager
    def _create_connection(self):
        """
        Create a database connection to a SQLite database.

        Args:
            db_file: The database file to connect to.

        Yields:
            The database connection.
        """
        conn = sqlite3.connect(self.path)
        try:
            cursor =  conn.cursor()
            yield cursor
        finally:
            logging.info("Closing connection to database.")
            conn.commit()
            conn.close()

    def print_table(self, table_name: str, sql_query: str = "", cols: str = "") -> None:
        """
        Print the contents of a table in the database using package PrettyTable.
        By default, prints the entire table, but can be modified to print a subset of the table.

        Args:
            database_name: The name of the database to print the table from.
            table_name: The name of the table to print.
            sql_query: The SQL query to use to print the table (default is none, which prints the entire table).
            cols: The names of the columns to print (default is none, which prints all columns).
        """
        with self._create_connection() as c:

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
                        logging.error(f"Table {table_name} does not exist in database {self.path}.")
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

    def _insert_into_table(self, table_name: str, values: list, cols: list = [] )-> int:
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
        with self._create_connection() as c:

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

    def _create_empty_database(self, path, excluded_cols: list = []) -> None:
        self.path = path
        with self._create_connection() as c:
            # Payment types table (stores the names of the payment types eg: Visa, Cash, etc...)
            c.execute("""CREATE TABLE IF NOT EXISTS accounts (
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT
            )""")

            # Categories table (stores category and subcategory of an expense, eg: groceries, rent, etc...)
            # Checking for any columns the user does NOT want to use
            create_expense_commands = {
                'id': "id INTEGER PRIMARY KEY AUTOINCREMENT",
                'item': "item TEXT NOT NULL",
                'amount': "amount REAL NOT NULL",
                'type': "type TEXT NOT NULL CONSTRAINT valid_type CHECK(Type IN ('want', 'need', 'savings'))",
                'receipt_id': "receipt_id INTEGER NOT NULL",
                'category_id': "category_id INTEGER NOT NULL",
                'details': "details TEXT",
                "receipt_id_fk": "FOREIGN KEY(receipt_id) REFERENCES receipts(id)",
                "category_id_fk": "FOREIGN KEY(category_id) REFERENCES categories(id)"
            }
            expenses = "CREATE TABLE IF NOT EXISTS expenses ("
            for key, value in create_expense_commands.items():
                if key not in excluded_cols:
                    if key == "category_id_fk" and "category_id" in excluded_cols:
                        continue
                    expenses += f"{value}, "
            expenses = expenses[:-2] + ")"

            if "category_id" not in excluded_cols:
                c.execute("""CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    category TEXT NOT NULL,
                    subcategory TEXT
                )""")

            # Expenses table (stores details about a single expense eg: details on each item of a receipt)
            c.execute(expenses)

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
                FOREIGN KEY (account_id) REFERENCES accounts(id)
            )""")
            
            # Income table (stores details about income eg: income from a job, etc...)
            if "income_details" not in excluded_cols:
                c.execute("""CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    paystub_id INTEGER NOT NULL,
                    details TEXT,
                    FOREIGN KEY (paystub_id) REFERENCES paystubs(id)
                )""")
            else:
                c.execute("""CREATE TABLE IF NOT EXISTS incomes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    amount REAL NOT NULL,
                    paystub_id INTEGER NOT NULL,
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

    def _get_tables(self) -> list:
        """"
        Returns a list of all tables in the database.

        Returns:
            list: A list of all tables in the database.
        """
        with self._create_connection() as c:
            c.execute("SELECT name FROM sqlite_master WHERE type='table'")
            # For some reason, "sqlite_sequence" is in the list of tables so we filter it out
            return [table[0] for table in c.fetchall() if table[0] != "sqlite_sequence"]

    def query_db(self, sql_query: str) -> list:
        """
        Query the database and return the results.

        Args:
            database_name: The name of the database to query.
            sql_query: The SQL query to use to query the database.

        Returns:
            A list of the results of the query.
        """
        with self._create_connection() as c:
            try:
                c.execute(sql_query)
            except sqlite3.OperationalError as e:
                logging.error(f"Invalid SQL query. See error message -> {e}")
                return []

            return c.fetchall()

    def _search_expenses(self, expense_item: str = "", days: str = 365)-> dict:
        """
        Searches for the expense in the database.

        Args:
            database_name: The name of the database to search.
            expense_item: The item to search for.
            days: How many days to limit the search to.

        Returns:
            A list of the expense names that fit the criteria.
        """
        with self._create_connection() as c:
            if not expense_item:
                c.execute(f"""
                SELECT *  \
                    FROM receipts INNER JOIN (SELECT * FROM expenses e1 WHERE NOT EXISTS \
                        (SELECT * FROM expenses e2 WHERE e1.item = e2.item and e2.id < e1.id)) e ON receipts.id = e.receipt_id\
                    WHERE JulianDay('now') - JulianDay(date) <= {days}""")
            else:
                c.execute(f"""
                SELECT *\
                    FROM receipts INNER JOIN (SELECT * FROM expenses e1 WHERE NOT EXISTS \
                        (SELECT * FROM expenses e2 WHERE e1.item = e2.item and e2.id < e1.id)) e ON receipts.id = e.receipt_id\
                    WHERE JulianDay('now') - JulianDay(date) <= {days} AND item = '{expense_item}'""")
            result = {col_data[0]: [] for col_data in c.description}
            for row in c.fetchall():
                for col_index, col_data in enumerate(row):
                    result[c.description[col_index][0]].append(col_data)
            return result

    def _search_categories(self, category_ids: list[int] = []) -> dict:
        """
        Search for a category in the database.

        Args:
            database_name: The name of the database to search in.
            category_id: The category to search for.

        Returns:
            A dictionary of values for the list of category ids. If no list is specified, all categories are returned.
        """
        with self._create_connection() as c:
            if not category_ids:
                c.execute("SELECT * FROM categories")
            else:
                c.execute(f"SELECT * FROM categories WHERE id IN { '(' + str(category_ids)[1:-1] + ')'}")
            result = {col_data[0]: [] for col_data in c.description}
            for row in c.fetchall():
                for col_index, col_data in enumerate(row):
                    result[c.description[col_index][0]].append(col_data)
            return result

    def _search_paystubs(self, paystub_id: int = None, payer: str = "", date: str = "") -> dict:
        """
        Search for a paystub in the database.

        Args:
            database_name: The name of the database to search in.
            paystub_id: The paystub to search for.
            payer: The payer to search for.
            date: The date to search for.

        Returns:
            A dictionary of values for the paystub.
        """
        with self._create_connection() as c:
            if paystub_id:
                c.execute(f"SELECT * FROM paystubs WHERE id = {paystub_id}")
            elif payer:
                c.execute(f"SELECT * FROM paystubs WHERE payer = '{payer}'")
            elif date:
                c.execute(f"SELECT * FROM paystubs WHERE date = '{date}'")
            else:
                c.execute("SELECT * FROM paystubs")
            result = {col_data[0]: [] for col_data in c.description}
            for row in c.fetchall():
                for col_index, col_data in enumerate(row):
                    result[c.description[col_index][0]].append(col_data)
            return result

    def _search_incomes(self, income_id: int = None) -> dict:
        """
        Search for an income in the database.

        Args:
            database_name: The name of the database to search in.
            income_id: The income to search for.
            payer: The payer to search for.
            date: The date to search for.

        Returns:
            A dictionary of values for the income.
        """
        with self._create_connection() as c:
            if income_id:
                c.execute(f"SELECT * FROM incomes WHERE id = {income_id}")
            else:
                c.execute("SELECT * FROM incomes")
            result = {col_data[0]: [] for col_data in c.description}
            for row in c.fetchall():
                for col_index, col_data in enumerate(row):
                    result[c.description[col_index][0]].append(col_data)
            return result

    def delete_row(self, table_name: str, row_id: int) -> None:
        """
        Delete a row from the database.

        Args:
            database_name: The name of the database to delete from.
        """
        with self._create_connection() as c:
            c.execute(f"DELETE FROM {table_name} WHERE id = '{row_id}'")
