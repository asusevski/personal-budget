from program import Program
from program_menus import IndexMenu, MainMenu, TableMenu
from cli import CLI


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
    main_menu_options = ["Initialize database", "Insert expense transaction", "Insert income transaction", "Print table", "Delete row", \
                         "Execute arbitrary sql query", "Exit"]
    table_options = ["accounts", "categories", "expenses", "receipts", "ledger",  "incomes", "paystubs", "paystub_ledgers"]
    main_menu = MainMenu(options=main_menu_options)
    table_menu = TableMenu(options=table_options)
    index_menu = IndexMenu(options=table_options)
    cli = CLI()
    Program(cli, main_menu, table_menu, index_menu).run()


if __name__ == "__main__":
    main()
