from Program.program import Program
from UI.cli import CLI


def main():
    """
    Interface to create, update, and maintain sqlite database budget.db (default name)

    User can:
        - Insert expenses into expenses table
        - Insert income into income table
        - Print a table
        - Delete a row from a table
        - Execute an arbitrary sql query
        - Exit

    """
    cli = CLI()
    Program(cli).run()


if __name__ == "__main__":
    main()
