def create_table(database_name: str, table_name: str, **kwargs) -> None:
    """
    Create a table in the database.

    Parameters:
        table_name (str): The name of the table to create.
        kwargs (dict): The arguments to pass to the table creation.

    Returns:
        None

    Requires:
        The first key(s) in the kwargs dictionary are the primary key of the table.
    """
    import sqlite3

    # Create a database connection
    conn = sqlite3.connect(database_name)
    c = conn.cursor()

    # Create table
    pairs = [(k, v) for k, v in kwargs.items()]
    str = ""
    for pair in pairs:
        str += f"{pair[0]} {pair[1]}, "
    str = str[:-2]
    c.execute(f"CREATE TABLE IF NOT EXISTS {table_name} ({str})")

    # Save (commit) the changes
    conn.commit()

    # Close the connection
    conn.close()