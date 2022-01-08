def create_table(database_name: str, table_name: str, cols: dict, constraints: dict) -> None:
    """
    Create a table in the database.

    Parameters:
        database_name (str): Name of the database.
        table_name (str): The name of the table to create.
        cols (dict): The arguments to pass to the table creation.

    Returns:
        None

    Requires:
        The first key(s) in the kwargs dictionary are the primary key of the table.
    
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