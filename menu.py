from typing import Protocol


class Menu(Protocol):
    def _print_menu(self) -> None:
        pass
    
    def _read_choice(self) -> int:
        pass
    
    def _handle_choice(self, choice: int) -> None:
        pass
    
    def run(self) -> None:
        self._print_menu()
        choice = self._read_choice()
        self._handle_choice(choice)

