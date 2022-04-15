from dataclasses import dataclass
from UI.menu import Menu
from UI.ui import UI


@dataclass
class Program:
    ui : UI
    main_menu : Menu
    table_menu: Menu
    index_menu: Menu

    def run(self) -> None:
        while True:
            choice = self.main_menu.run()
            if choice == 1:
                self.ui.initialize_db()
            elif choice == 2:
                self.ui.insert_expense_transactions()
            elif choice == 3:
                self.ui.insert_income_transaction()
            elif choice == 4:
                self.ui.print_table(self.table_menu)
            elif choice == 5:
                self.ui.delete_row(self.index_menu)
            elif choice == 6:
                self.ui.execute_sql_query()
            elif choice == 7:
                self.ui.exit()
