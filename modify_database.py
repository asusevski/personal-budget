def create_table(database_name: str, table_name: str, cols: dict, constraints: dict) -> None:
    """
    Create a table in the database.

    Parameters:
        database_name (str): Name of the database.
        table_name (str): The name of the table to create.
        cols (dict): The names of the columns in the table that will be created.
        constraints (dict): The constraints to be applied to the columns (eg. PRIMARY KEY etc).

    Returns:
        None
    
    Effects:
        Creates a table in the database.
    """
    import sqlite3

    # Create a database connection
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    # Create table
    col_pairs = [(k, v) for k, v in cols.items()]
    str = ""
    for pair in col_pairs:
        if pair[0] in constraints.keys():
            str += f"{pair[0]} {pair[1]} {constraints[pair[0]]}, "
        else:
            str += f"{pair[0]} {pair[1]}, "
    str = str[:-2]
    c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({str})")

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()


def insert_record(database_name: str, table_name: str, vals: list, cols: list = []) -> None:
    import sqlite3

    # Create a database connection
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    # If unspecified columns to insert values into, then don't use cols
    # Otherwise, if inserting only some columns (ie: perhaps ignoring ID row)
    # then specify what columns to insert
    print("columns:", cols)
    print("vals:", vals)
    if cols == []:
        c.execute(f'''INSERT INTO {table_name} VALUES ({str(vals)[1:-1]})''')

        # Save (commit) the changes
        conn.commit()

        # Close the connection
        conn.close()
    else:
        c.execute(f'''INSERT INTO {table_name} ({str(cols)[1:-1]}) VALUES ({str(vals)[1:-1]})''')

        # Save (commit) the changes
        conn.commit()

        # Close the connection
        conn.close()


def insert_record_old(database_name: str, table_name: str) -> None:
    """
    Inserts a row into a table in the database.

    Parameters:
        database_name (str): Name of the database.
        table_name (str): The name of the table to insert record into.

    Returns:
        None

    Effects:
        Inserts a row into a table in the database.
    """
    import sqlite3

    # Create a database connection
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    # Print the columns of the table:
    data = c.execute(f'''SELECT * FROM {table_name}''')
    col_names = [description[0] for description in data.description]
    print(f"Columns in table: {col_names}")

    

    while True:

        # Get the user's input
        vals = []
        for col_name in col_names:
            user_input = input(f'Enter {col_name}: ')
            if user_input == "q":
                # Save (commit) the changes
                conn.commit()

                # Close the connection
                conn.close()
                return
            vals.append(user_input)

        # Insert a row of data
        c.execute(f'''INSERT INTO {table_name} VALUES ({str(vals)[1:-1]})''')
