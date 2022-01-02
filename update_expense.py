from create_table import create_table
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
        2. Add an expense
        3. Exit
        """)
        choice = input("Enter your choice: ")
        if choice == "1":
            database_name = input("Enter database name: ")
            table_name = input("Table name: ")

            kwargs = {}
            print("Enter primary keys of table first, followed by all other columns.")
            
            while True:
                colname = input("Enter column name or q if done: ")
                if colname.lower() == "q":
                    break
                if colname in kwargs.keys():
                    print("Colname exists already, try again.")
                    continue
                print("Datatypes are one of {INTEGER, REAL, TEXT, BLOB}")
                coltype = input("Enter datatype of column: ")
                kwargs[colname] = coltype
            
            create_table(database_name, table_name, kwargs)
        elif choice == "2":
            #add_expense()
            pass
        elif choice == "3":
            sys.exit()
        else:
            print("Invalid choice")
            continue

    # Get the user's input
    expense_name = input('Enter the name of the expense: ')
    expense_amount = input('Enter the amount of the expense: ')
    expense_date = input('Enter the date of the expense (YYYY-MM-DD): ')
    expense_date = datetime.strptime(expense_date, '%Y-%m-%d')
    expense_frequency = input('Enter the frequency of the expense (daily, weekly, monthly, yearly): ')

    # Insert the expense into the database
    c.execute('INSERT INTO expenses VALUES (?, ?, ?, ?, ?)', (expense_name, expense_amount, expense_date, expense_frequency, 0))
    conn.commit()

    # Close the connection
    conn.close()

if __name__ == "__main__":
    main()
