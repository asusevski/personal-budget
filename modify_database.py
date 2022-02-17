from contextlib import contextmanager
import logging
import sqlite3

@contextmanager
def create_connection(db_file: str):
    """
    Create a database connection to a SQLite database.
    :param db_file: The database file to connect to.
    :return: The database connection.
    """
    conn = sqlite3.connect(db_file)
    try:
        cursor =  conn.cursor()
        yield cursor
    finally:
        logging.info("Closing connection to database.")
        conn.commit()
        conn.close()

