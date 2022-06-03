from Database.database import Database
from dataclasses import dataclass
from UI.ui import UI


@dataclass
class Program:
    """
    Program is a class to handle the high level program functions. 
    Upon initializing, Program initializes a Database object and,
    if there is no database file (.sqlite or .db) found in a subdirectory, 
    the UI handles initializing a database.

    Attributes:
        ui: UI
        database: Database
    
    """
    ui : UI
    database: Database

    def __init__(self, ui: UI) -> None:
        self.ui = ui
        db = Database()
        if not db.path:
            db = self.ui._initialize_db(db)
        self.database = db

    def run(self) -> None:
        self.ui.run(self.database)
