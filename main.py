from categories import ExpenseCategory, Account
from interface import _find_db, read_income_transaction_from_user, read_expense_transaction_from_user
from manage_database import delete_row, initialize_empty_db, print_table, query_db
import sys


def main():
    """
    Interface to create, update, and maintain sqlite database budget.db (default name)

    User can:
        - Initialize basic tables in a budget database
        - Insert expenses into expenses table
        - Insert income into income table
        - Print a table
        - Delete a row from a table
        - Execute an arbitrary sql query

    """
    while True:
        print("""

1. Initialize budget database
2. Insert expenses into expenses table
3. Insert incomes in incomes table
4. Print a table
5. Delete a row from a table
6. Execute an SQL Query
7. Exit

        """)
        print("Enter your choice: ")
        choice = input("> ")

        
        if choice == "2":
            database_name = _find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            print("Enter q at any time to stop entering transactions.")
            while True:
                expense_transaction = read_expense_transaction_from_user(database_name)
                if not expense_transaction:
                    print("Transaction cancelled.")
                    break
                else:
                    # Insert transaction into database
                    retval = expense_transaction.execute(database_name)
                    if not retval:
                        print("Transaction added to database.")
                    else:
                        print(f"Transaction failed to be added. Error message: {retval}")

        if choice == "3":
            database_name = _find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            print("Enter q at any time to stop entering income transactions.")
            while True:
                income_transaction = read_income_transaction_from_user(database_name)
                if not income_transaction:
                    print("Transaction cancelled.")
                    break
                else:
                    # Insert transaction into database
                    retval = income_transaction.execute(database_name)
                    if not retval:
                        print("Income transaction added.")
                    else:
                        print(f"Income transaction failed to be added. Error message: {retval}")
        
        if choice == "4":
            database_name = _find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            print("""Table Names in database: 
            
1. accounts
2. categories
3. expenses
4. receipts
5. ledger
6. incomes
7. paystubs
8. paystub_ledger

            """)
            
            print("Enter table name to print: ")
            table_name = input("> ")
            print_table(database_name, table_name)

        if choice == "5":
            database_name = _find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            print("Enter table from which to delete a row: ")
            table_name = input("> ")
            print_table(database_name, table_name)
            print("Enter row id to delete: ")
            row_id = input("> ")
            delete_row(database_name, table_name, row_id)
            print("Row deleted.")

        if choice == "6":
            database_name = _find_db()
            if not database_name:
                print("No database found. Please intialize a database first.")
                continue

            print("Enter SQL query: ")
            sql_query = input("> ")
            print("Executing query...")
            vals = query_db(database_name, sql_query)
            print(f"Results: {vals}")

        # Quit
        if choice == "7":
            sys.exit()


if __name__ == "__main__":
    main()