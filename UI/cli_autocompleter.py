from prompt_toolkit.completion import Completer, Completion #, FuzzyCompleter


class CustomCompleter(Completer):
    def __init__(self, words: list[str]):
        self.words = words

    def get_completions(self, document, complete_event):
        word = document.get_word_before_cursor()
        for expense_name in self.words:
            if expense_name.startswith(word):
                yield Completion(
                    expense_name, 
                    start_position=-len(document.text)
                )
                