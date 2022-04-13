from manage_database import print_table
from typing import Tuple


class MainMenu():
    def __init__(self, options: list):
        self.options = options

    def print_menu_and_read_choice(self) -> int:
        s = "Select an option:\n"
        for i, option in enumerate(self.options):
            s += f"{i + 1}. {option}\n"
        print(s)

        choice = input("> ")
        if not choice.isnumeric():
            try:
                choice = int(self.options.index(choice)) + 1
            except ValueError:
                print("Invalid choice. Please try again.")
                return None
        elif int(choice) > len(self.options):
            print("Invalid choice. Please try again.")
            return None
        return int(choice)

    def handle_choice(self, choice: str) -> str:
        return choice

    def run(self) -> int:
        choice = self.print_menu_and_read_choice()
        return self.handle_choice(choice)


class TableMenu():
    def __init__(self, options: list):
        self.options = options

    def print_menu_and_read_choice(self) -> str:
        # This differs from the implementation in the MainMenu class because here we return the table name
        s = "Select an option:\n"
        for i, option in enumerate(self.options):
            s += f"{i + 1}. {option}\n"
        print(s)

        choice = input("> ")
        if choice.isnumeric():
            try:
                choice = self.options[int(choice) - 1]
            except ValueError:
                print("Invalid choice. Please try again.")
                return None
        elif choice not in self.options:
            print("Invalid choice. Please try again.")
            return None
        
        return choice

    def handle_choice(self, choice: str) -> str:
        return choice

    def run(self) -> str:
        choice = self.print_menu_and_read_choice()
        return self.handle_choice(choice)


class IndexMenu(TableMenu):
    def __init__(self, options: list):
        super().__init__(options)

    def read_index(self, database_name: str, table_name: str) -> int:
        print_table(database_name, table_name)
        print(f"Enter index of row to delete:")
        index = input("> ")
        if not index.isnumeric():
            print("Invalid index. Please try again.")
            return None
        return int(index)

    def handle_choice(self, choice: Tuple[str, int]) -> int:
        return choice

    def run(self, database_name: str) -> str:
        choice = super().print_menu_and_read_choice()
        index = self.read_index(database_name, choice)
        return self.handle_choice((choice, index))
