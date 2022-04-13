from typing import Any, Protocol


class Menu(Protocol):
    def print_menu(self) -> None:
        ...
    
    def read_choice(self) -> Any:
        ...
    
    def handle_choice(self, choice: Any) -> Any:
        ...
    
    def run(self) -> Any:
        self.print_menu()
        choice = self.read_choice()
        self.handle_choice(choice)
