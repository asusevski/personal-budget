from typing import Any, Protocol


class Menu(Protocol):
    def print_menu_and_read_choice(self) -> Any:
        ...
    
    def handle_choice(self, choice: Any) -> Any:
        ...

    def run(self) -> Any:
        choice = self.print_menu_and_read_choice()
        return self.handle_choice(choice)
