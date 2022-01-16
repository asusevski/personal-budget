from budget import create_expenses
from budget import create_categories
from budget import create_payment
from modify_database import create_table
from modify_database import insert_record
import sqlite3
import sys


# Constants:
HST_TAX_RATE = 0.13


def main():
    """
    Interface to create, update, and maintain sqlite database budget.db (default name)

    User can:
        - Initialize basic tables in a budget database
        - Create table in database
        - Insert single expense into expenses table
        - Insert receipt of expenses into expenses table

    """
    while True:
        print("""

        1. Initialize budget database
        2. Create a new table
        3. Insert rows into any table
        4. Insert expenses into expenses table
        5. Insert a receipt of expenses into expenses table
        6. Exit

        """)
        choice = input("Enter your choice: ")

        # Initialize budget database
        if choice == "1":
            database_name = input("Enter database name (default name is budget): ")

            # If no custome database name is entered, use default name
            if database_name == "":
                database_name = "budget"

            # Adding suffix to database name
            if database_name[-3:] != ".db" or ".sqlite" not in database_name:
                database_name += ".db"

            # Create basic tables
            create_expenses(database_name)
            create_categories(database_name)
            create_payment(database_name)
        
        # Create custom table in db
        if choice == "2":
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
                while coltype.lower() not in ["integer", "real", "text", "blob"]:
                    coltype = input("Invalid data type. Enter datatype of column: ")
                cols[colname] = coltype

                constraint = input("Enter constraint(s) (e.g. PRIMARY KEY, NOT NULL, UNIQUE) or q if none: ")
                if constraint.lower() == "q" or constraint == "": 
                    continue
                
                constraints[colname] = constraint
                
            create_table(database_name, table_name, cols, constraints)

        # Insert rows into any table
        if choice == "3":
            database_name = input("Enter database name: ")
            if database_name[-3:] != ".db" or ".sqlite" in database_name:
                database_name += ".db"
            table_name = input("Table name: ")
            
            conn = sqlite3.connect(database_name)
            c = conn.cursor()

            data = c.execute(f'''SELECT * FROM {table_name}''')
            col_names = [description[0] for description in data.description]

            # Usually, we don't want to have to enter the ID of the row we're adding. However, that option
            # will be left in since it's possible that we would want to add a row with a specific ID.
            specific_id = input("Do you want to enter a specific ID? (y/n): ")
            if specific_id.lower() == "n":
                col_names.remove("ID")
            
            print(f"Columns in table: {col_names}")

            while True:

                # Get the user's input
                vals = []
                for col_name in col_names:
                    user_input = input(f'Enter {col_name}: ')
                    vals.append(user_input)

                # Insert a row of data
                insert_record(database_name=database_name, table_name=table_name, vals=vals, cols=col_names)
                print("Record inserted.")

                user_input = input('Enter q to quit or any other key to continue entering expenses: ')
                if user_input == "q":
                    conn.commit()
                    c.close()
                    break

        # Insert expenses into expenses table
        if choice == "4":
            database_name = input("Enter database name: ")
            if database_name[-3:] != ".db" or ".sqlite" not in database_name:
                database_name += ".db"
        
            table_name = "expenses"

            # Create a database connection
            conn = sqlite3.connect(database_name)
            c = conn.cursor()

            # Print the columns of the table:
            data = c.execute(f'''SELECT * FROM {table_name}''')
            col_names = [description[0] for description in data.description]

            # Removing ID since the ID col is autoincrement, we don't have to add it ourselves
            col_names.remove("ID")

            print(f"Columns in table: {col_names}")

            while True:

                # Get the user's input
                vals = []
                for col_name in col_names:
                    user_input = input(f'Enter {col_name}: ')
                    vals.append(user_input)

                # Insert a row of data
                insert_record(database_name=database_name, table_name=table_name, vals=vals, cols=col_names)
                print("Record inserted.")

                user_input = input('Enter q to quit or any other key to continue entering expenses: ')
                if user_input == "q":
                    conn.commit()
                    c.close()
                    break

        # Insert a receipt of expenses into expenses table
        if choice == "5":
            database_name = input("Enter database name: ")
            if database_name[-3:] != ".db" or ".sqlite" not in database_name:
                database_name += ".db"
        
            table_name = "expenses"

            # Get receipt info
            receipt_date = input("Enter receipt date: ")
            receipt_location = input("Enter receipt location: ")
            receipt_payment = input("Enter receipt Payment ID: ")

            # Create a database connection
            conn = sqlite3.connect(database_name)
            c = conn.cursor()

            # Print the columns of the table:
            data = c.execute(f'''SELECT * FROM {table_name}''')
            col_names = [description[0] for description in data.description]

            # Removing ID since the ID col is autoincrement, we don't have to add it ourselves
            # Also removing the columns we found above (col_names_input will be the names of the columns 
            # that we actually need to insert specifically)
            col_names_input = [col_name for col_name in col_names if col_name not in ["ID", "Date", "Location", "Payment_ID"]]

            print(f"Columns in table: {col_names}")

            while True:

                # Get the user's input
                vals = []
                for col_name in col_names_input:
                    if col_name == "Amount":
                        user_input = input(f'Enter {col_name}: ')

                        discount = input('Enter discount as a percent (without the percent sign) if applicable: ')
                        taxable = input('Is this expense taxable? (y/n): ')

                        if discount != "":
                            user_input = float(user_input) * (1 - float(discount) / 100)
                            user_input = str(round(user_input, 2))

                        if taxable == 'y':
                            user_input = float(user_input) * (1 + HST_TAX_RATE)
                            # Convert user_input to a two decimal point float and then to a string
                            user_input = str(round(user_input, 2))
                        
                        vals.append(user_input)
                        continue

                    user_input = input(f'Enter {col_name}: ')
                    vals.append(user_input)

                # Adding receipt info to vals
                vals.insert(0, receipt_date)
                vals.insert(2, receipt_location)
                vals.insert(3, receipt_payment)

                # Insert a row of data
                insert_record(database_name=database_name, table_name=table_name, vals=vals, cols=col_names)
                print("Record inserted.")

                user_input = input('Enter q to quit or any other key to continue entering expenses: ')
                if user_input == "q":
                    conn.commit()
                    c.close()
                    break
        
        # Exit
        if choice == "6":
            sys.exit()


def main_old():
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
                while coltype.lower() not in ["integer", "real", "text", "blob"]:
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
