"""
This module provides a graphical user interface (GUI) application for the Spellcast Word Finder.

It utilizes the tkinter library for creating the GUI elements and interacts with the
Spellcast WordBoard class to generate words based on user input.

Classes:
    SpellcastApp: Represents the main application class for the Spellcast Word Finder.

Functions:
    None

Usage:
    To use this module, create an instance of the SpellcastApp class and run the application.

Example:
    import tkinter as tk
    from spellcast_app import SpellcastApp

    if __name__ == "__main__":
        root = tk.Tk()
        app = SpellcastApp(root)
        root.mainloop()
"""

import tkinter as tk
import tkinter.font as tkFont
from spellcast import WordBoard


class SpellcastApp:
    """
    A class representing the Spellcast Word Finder application.

    Attributes:
        word_board (WordBoard): An instance of the WordBoard class.

    Methods:
        __init__(self, app_window): Initializes the SpellcastApp object.
        on_validate(new_value, row, column): Validates the input in the entry fields.
        generate_words_command(self): Generates words based on the input values.
        add_multiplier(self, row, col, word=False): Adds a multiplier to a specific cell.
        remove_multiplier(self, row, col): Removes a multiplier from a specific cell.
    """

    def __init__(self, app_window):
        """
        Initializes the SpellcastApp object.

        Args:
            app_window (tk.Tk): The main application window.
        """
        self.word_board = WordBoard()

        app_window.title("Spellcast Word Finder")
        width = 600
        height = 256
        screen_width = app_window.winfo_screenwidth()
        screen_height = app_window.winfo_screenheight()
        window_position = "%dx%d+%d+%d" % (
            width,
            height,
            (screen_width - width) / 2,
            (screen_height - height) / 2,
        )
        app_window.geometry(window_position)
        app_window.resizable(width=False, height=False)

        self.values = [
            [tk.StringVar(app_window, value="") for _ in range(5)] for _ in range(5)
        ]
        self.line_inputs = []
        self.labels = []

        def on_validate(new_value, row, column):
            """
            Validates the input in the entry fields.

            Args:
                new_value (str): The new value entered in the entry field.
                row (int): The row index of the entry field.
                column (int): The column index of the entry field.

            Returns:
                bool: True if the input is valid, False otherwise.
            """
            row, column = map(int, (row, column))
            index = (row * 5 + column + 1) % 25
            if len(new_value) == 1:
                self.line_inputs[index].focus_set()
                self.line_inputs[index].select_range(0, "end")
            return True

        x_offset, y_offset = 25, 25
        for row in range(5):
            for column in range(5):
                entry = tk.Entry(
                    app_window,
                    textvariable=self.values[row][column],
                    validate="key",
                    highlightthickness=2,
                )
                entry["borderwidth"] = "1px"
                entry["font"] = tkFont.Font(family="Times", size=10)
                entry["fg"] = "#333333"
                entry["justify"] = "center"
                entry["validatecommand"] = (
                    entry.register(on_validate),
                    "%P",
                    row,
                    column,
                )
                entry.place(
                    x=x_offset + column * 32, y=y_offset + row * 32, width=32, height=32
                )
                entry.configure(
                    highlightbackground="black",
                    highlightcolor="black",
                    font=("Roboto", 16),
                )
                self.line_inputs.append(entry)

        for row in range(3):
            label = tk.Label(app_window)
            label["font"] = tkFont.Font(family="Times", size=10)
            label["fg"] = "#333333"
            label["justify"] = "center"
            label["text"] = ""
            label.place(x=320, y=80 + row * 30, width=250, height=25)
            self.labels.append(label)

        button = tk.Button(app_window)
        button["bg"] = "#e9e9ed"
        button["font"] = tkFont.Font(family="Times", size=10)
        button["fg"] = "#000000"
        button["justify"] = "center"
        button["text"] = "Generate Words"
        button.place(x=x_offset, y=y_offset + 160, width=160, height=25)
        button["command"] = self.generate_words_command

    class LabelHover:
        """
        A class representing the hover effect for labels.

        Attributes:
            label (tk.Label): The label to apply the hover effect to.
            path (str): The path of the word.
            skipped (list): The list of skipped cells in the word.
            line_inputs (list): The list of entry fields.
            values (list): The list of StringVars representing the values in the entry fields.
            word (str): The word associated with the label.

        Methods:
            hover(self): Applies the hover effect to the label.
            unhover(self): Removes the hover effect from the label.
        """

        def __init__(self, label, path, skipped, line_inputs, values, word):
            """
            Initializes the LabelHover object.

            Args:
                label (tk.Label): The label to apply the hover effect to.
                path (str): The path of the word.
                skipped (list): The list of skipped cells in the word.
                line_inputs (list): The list of entry fields.
                values (list): The list of StringVars representing the values in the entry fields.
                word (str): The word associated with the label.
            """
            self.label = label
            self.path = path
            self.skipped = skipped
            self.skip_set = set(skipped)
            self.line_inputs = line_inputs
            self.label.bind("<Enter>", lambda _: self.hover())
            self.label.bind("<Leave>", lambda _: self.unhover())
            self.values = values
            self.temporary = [
                [value.get().lower() for value in line] for line in self.values
            ]
            self.word = word

        def hover(self):
            """
            Applies the hover effect to the label.
            """
            for (i, j), c in zip(self.path[::-1], self.word):
                entry_index = i * 5 + j
                self.line_inputs[entry_index].configure(
                    highlightbackground="blue",
                    highlightcolor="blue",
                    background="blue",
                    font=("Roboto", 20, tkFont.BOLD),
                    fg="white",
                )
                if (i, j) in self.skip_set:
                    self.values[i][j].set(c)

            for i, j in self.skipped:
                entry_index = i * 5 + j
                self.line_inputs[entry_index].configure(
                    highlightbackground="red",
                    highlightcolor="red",
                    background="red",
                    font=("Roboto", 20, tkFont.BOLD),
                    fg="white",
                )

        def unhover(self):
            """
            Removes the hover effect from the label.
            """
            for i, j in self.path + self.skipped:
                entry_index = i * 5 + j
                self.line_inputs[entry_index].configure(
                    highlightbackground="black",
                    highlightcolor="black",
                    background="white",
                    font=("Roboto", 16, tkFont.NORMAL),
                    fg="black",
                )
                self.values[i][j].set(self.temporary[i][j])

    def generate_words_command(self):
        """
        Generates words based on the input values.
        """
        board = [[v.get().lower() for v in line] for line in self.values]
        self.word_board.set_board(board)

        words = [
            self.word_board.best_word(i)
            for i in range(3)  # (best word, value, path, skipped)
        ]

        word_label_prefix = ["No swaps", "One swap", "Two swaps"]

        for i, word in enumerate(words):
            self.labels[i]["text"] = f"{word_label_prefix[i]}: {word[:2]}"
            self.LabelHover(
                self.labels[i], word[2], word[3], self.line_inputs, self.values, word[0]
            )

    def add_multiplier(self, row, col, word=False):
        """
        Adds a multiplier to a specific cell.

        Args:
            row (int): The row index of the cell.
            col (int): The column index of the cell.
            word (bool): Whether the multiplier is for a word or a letter. Default is False.
        """
        self.word_board.add_multiplier(row, col, 1)

    def remove_multiplier(self, row, col):
        """
        Removes a multiplier from a specific cell.

        Args:
            row (int): The row index of the cell.
            col (int): The column index of the cell.
        """
        self.word_board.remove_multiplier(row, col)


if __name__ == "__main__":
    root = tk.Tk()
    app = SpellcastApp(root)
    root.mainloop()
