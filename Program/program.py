from Database.database import Database
from dataclasses import dataclass
from UI.menu import Menu
from UI.program_menus import IndexMenu, MainMenu, TableMenu
from UI.ui import UI


@dataclass
class Program:
    ui : UI
    database: Database
    main_menu : Menu
    table_menu: Menu
    index_menu: Menu

    def __init__(self, ui: UI) -> None:
        self.ui = ui
        db = Database()
        if not db.path:
            db = self.ui._initialize_db(db)
        self.database = db
        main_menu_options = ["Insert expense transaction", "Insert income transaction", "Print table", "Delete row", \
                         "Execute arbitrary sql query", "Exit"]
        self.main_menu = MainMenu(options=main_menu_options)
        table_options = self.database._get_tables()
        self.table_menu = TableMenu(options=table_options)
        self.index_menu = IndexMenu(options=table_options)

    def run(self) -> None:
        while True:
            choice = self.main_menu.run()
            if choice == 1:
                self.ui.insert_expense_transactions(self.database)
            elif choice == 2:
                self.ui.insert_income_transactions(self.database)
            elif choice == 3:
                self.ui.print_table(self.table_menu, self.database)
            elif choice == 4:
                self.ui.delete_row(self.index_menu)
            elif choice == 5:
                self.ui.execute_sql_query(self.database)
            elif choice == 6:
                self.ui.exit()
