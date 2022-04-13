class CLI():
    def _read_db_name(self) -> str:
        print("Enter database name (default name is budget): ")
        database_name = input("> ")
        # If no custome database name is entered, use default name
        if database_name == "":
            database_name = "budget"

        # Adding suffix to database name
        if ".db" not in database_name or ".sqlite" not in database_name:
            database_name += ".db"
            return database_name

        # Print name of database to confirm to user what name we're using
        print(f"Using database name: {database_name}")

        return database_name
    
    