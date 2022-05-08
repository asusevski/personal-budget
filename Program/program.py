import imp
from Database.database import Database
from dataclasses import dataclass
from UI.menu import Menu
from UI.ui import UI


@dataclass
class Program:
    ui : UI
    database: Database
    main_menu : Menu
    table_menu: Menu
    index_menu: Menu

    def __init__(self, ui: UI, main_menu: Menu, table_menu: Menu, index_menu: Menu) -> None:
        self.ui = ui
        db = Database()
        if not db.path:
            db = self.ui.initialize_db(db)
        self.database = db
        self.main_menu = main_menu
        self.table_menu = table_menu
        self.index_menu = index_menu

    def run(self) -> None:
        while True:
            choice = self.main_menu.run()
            if choice == 1:
                self.ui.initialize_db()
            elif choice == 2:
                self.ui.insert_expense_transactions()
            elif choice == 3:
                self.ui.insert_income_transactions()
            elif choice == 4:
                self.ui.print_table(self.table_menu)
            elif choice == 5:
                self.ui.delete_row(self.index_menu)
            elif choice == 6:
                self.ui.execute_sql_query()
            elif choice == 7:
                self.ui.exit()
