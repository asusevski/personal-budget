from budget import create_expenses
from modify_database import create_table
from modify_database import insert_record
import sys

def main():
    """
    Interface to update and maintain sqlite database budget.db (default name)

    User can:
        - Create table in database
        - Insert single expense into expenses table
        - Insert receipt of expenses into expenses table
    """
    while True:
        print("""
        1. Initialize budget database
        2. Create a new table
        3. Insert a single new expense
        4. Insert a receipt of expenses
        5. Exit
        """)
        choice = input("Enter your choice: ")

        # Initialize budget database
        if choice == "1":
            database_name = input("Enter database name (default name is budget): ")

            # Adding suffix to database name
            if database_name[-3:] != ".db" or ".sqlite" not in database_name:
                database_name += ".db"

            create_expenses(database_name)
        
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

# only one category column and categories table just have (ID, Subcategory, Category) but only keep subcategory in expenses
