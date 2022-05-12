from Database.database import Database
from dataclasses import dataclass
from UI.ui import UI


@dataclass
class Program:
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
