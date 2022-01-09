from modify_database import create_table
from modify_database import insert_record
import sqlite3
import sys
"""
from datetime import datetime
from datetime import date
from datetime import timedelta
from dateutil.parser import parse
from dateutil.relativedelta import relativedelta
from dateutil.relativedelta import MO
from dateutil.relativedelta import TU
from dateutil.relativedelta import WE
from dateutil.relativedelta import TH
from dateutil.relativedelta import FR
from dateutil.relativedelta import SA
from dateutil.relativedelta import SU
from dateutil.relativedelta import WEEKDAY  
from dateutil.rrule import rrule, MO, TU, WE, TH, FR, SA, SU
"""

def main():
    """
    Updates database expense.db with new expense or new table.
    """

    # Connect to the database
    #conn = sqlite3.connect('expenses.db')
    #c = conn.cursor()

    while True:
        print("""
        1. Create a table
        2. Insert record into a table
        3. Exit
        """)
        choice = input("Enter your choice: ")
        if choice == "1":
            database_name = input("Enter database name: ")
            if database_name[-3:] != ".db" or ".sqlite" in database_name:
                database_name += ".db"
            table_name = input("Table name: ")

            cols = {}
            constraints = {}
            
            while True:
                colname = input("Enter column name or q if done: ")
                if colname.lower() == "q":
                    break
                if colname in cols.keys():
                    print("Colname exists already, try again.")
                    continue
                print("Datatypes are one of {INTEGER, REAL, TEXT, BLOB}")
                coltype = input("Enter datatype of column: ")
                while coltype not in ["INTEGER", "REAL", "TEXT", "BLOB"]:
                    coltype = input("Invalid data type. Enter datatype of column: ")
                cols[colname] = coltype

                constraint = input("Enter constraint(s) (e.g. PRIMARY KEY, NOT NULL, UNIQUE) or q if none: ")
                if constraint.lower() == "q" or constraint == "": 
                    continue
                
                constraints[colname] = constraint
                
            create_table(database_name, table_name, cols, constraints)

        elif choice == "2":
            database_name = input("Enter database name: ")
            if database_name[-3:] != ".db" or ".sqlite" in database_name:
                database_name += ".db"
            table_name = input("Table name: ")
            
            insert_record(database_name, table_name)

        elif choice == "3":
            sys.exit()
        else:
            print("Invalid choice")
            continue

if __name__ == "__main__":
    main()
