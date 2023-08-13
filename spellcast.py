"""
This module represents a word board game. It provides a class called `WordBoard`
that manages the logic for the game. The `WordBoard` class has various methods
for setting up the game board, finding the best word that can be formed on the board,
adding and removing multipliers, and performing preliminary checks for word validity.

Attributes:
    - `words` (list): A list of words loaded from the "words.txt" file.
    - `letter_values` (dict): A dictionary containing letter values considering multipliers.
    - `board_value` (dict): A dictionary containing values for each cell on the board.

Methods:
    - `__init__()`: Initializes a `WordBoard` instance by reading words from a file
    and initializing various attributes needed for managing the game board.
    - `recalculate()`: Recalculates letter values and board values based on the 
    current state of the board.
    - `set_board(board)`: Sets the game board and recalculates attributes based
    on the new board configuration.
    - `precheck(word)`: Performs a preliminary check for word validity
    by checking if the required letters for the word are available on the board.
    - `board_contains(word, skips=0)`: Checks if the board contains
    a given word, considering skips and multipliers.
    - `best_word(skips=0)`: Finds the highest scoring word that can be
    formed on the board, considering skips and multipliers.
    - `add_multiplier(row, column, multiplier, word)`: Adds a multiplier
    to a specific cell on the board and updates multipliers.
    - `remove_multiplier(row, column)`: Removes multipliers from a specific
    cell on the board and recalculates attributes.

Usage:
    - Create an instance of the `WordBoard` class.
    - Set the game board using the `set_board()` method.
    - Find the best words that can be formed on the board using the `best_word()` method.
    - Add or remove multipliers using the `add_multiplier()` and `remove_multiplier()` methods.
"""

from collections import Counter, defaultdict
from functools import reduce
from itertools import product
import threading

LETTERS_AND_VALUES = {
    "a": 1,
    "b": 4,
    "c": 5,
    "d": 3,
    "e": 1,
    "f": 5,
    "g": 3,
    "h": 4,
    "i": 1,
    "j": 7,
    "k": 3,
    "l": 3,
    "m": 4,
    "n": 2,
    "o": 1,
    "p": 4,
    "q": 8,
    "r": 2,
    "s": 2,
    "t": 2,
    "u": 4,
    "v": 5,
    "w": 5,
    "x": 7,
    "y": 4,
    "z": 8,
}


class WordBoard:
    """
    A class representing a word board game.

    This class manages the logic for a word board game, where players try to form words using
    letters on the board with different multipliers applied.

    Attributes:
        words_set (set): A set of words loaded from the "words.txt" file.
        letter_multipliers (defaultdict): A dictionary containing letter multipliers.
        word_multipliers (defaultdict): A dictionary containing word multipliers.
        board (list): A 2D list representing the game board.
        row_count (int): Number of rows on the board.
        column_count (int): Number of columns on the board.
        total_count (Counter): Count of each letter available on the board.
        word_values (list): A list of tuples containing word values and words.
        skips (int): Number of letters that can be skipped in forming a word.
    """

    def __init__(self):
        """
        Initializes a WordBoard instance.

        Reads words from a file and initializes various attributes needed for
        managing the game board.
        """
        self.words_set = set()
        self.letter_multipliers = defaultdict(lambda: 1)
        self.word_multipliers = defaultdict(lambda: 1)
        self.board = []
        self.row_count = 0
        self.column_count = 0
        self.total_count = Counter()
        self.word_values = []
        self.skips = 0

        with open("words.txt", encoding="utf-8") as file:
            self.words_set = {word[:-1] for word in file.readlines()}

    def recalculate(self):
        """
        Recalculate board-related attributes.

        This method recalculates letter values and board values based on the current state of the board.
        """
        max_global_multiplier = max(self.word_multipliers.values(), default=1)
        max_character_multiplier = defaultdict(lambda: 1)
        board_row_count = 5
        board_column_count = 5
        for row, column in product(range(board_row_count), range(board_column_count)):
            max_character_multiplier[self.board[row][column]] = max(
                max_character_multiplier[self.board[row][column]],
                max_global_multiplier,
                self.letter_multipliers[(row, column)],
            )

        letter_values = {
            letter: val * max_character_multiplier[letter]
            for letter, val in LETTERS_AND_VALUES.items()
        }

        long_word_bonus_points = 10
        long_word_minimum_letter_count = 6

        def calculate_value(word):
            value = sum(
                letter_values[character.lower()]
                for character in word
                if character.lower() in LETTERS_AND_VALUES
            ) + (
                        long_word_bonus_points if len(word) > long_word_minimum_letter_count else 0
                    )
            return value

        self.word_values = [(calculate_value(word), word) for word in self.words_set]
        self.word_values.sort(reverse=True)

    def set_board(self, game_board):
        """
        Set the game board.

        Args:
            game_board (list of lists): A 2D list representing the game board.

        Sets up the game board and recalculates attributes based on the new board configuration.
        """
        self.board = game_board
        self.row_count = len(game_board)
        self.column_count = len(game_board[0])
        self.total_count = Counter(cell for row in game_board for cell in row)

        self.word_multipliers = defaultdict(lambda: 1)
        self.letter_multipliers = defaultdict(lambda: 1)
        self.recalculate()

    def precheck(self, word):
        """
        Perform a preliminary check for word validity.

        Args:
            word (str): The word to be checked.

        Returns:
            bool: True if the word can be formed on the current board, False otherwise.

        Checks if the required letters for the word are available on the board.
        """
        word_count = Counter(word)
        for character in word_count:
            if word_count[character] > self.total_count[character]:
                return False
        return True

    def board_contains(self, word, skips=0):
        """
        Check if the board contains a given word.

        Args:
            word (str): The word to check for.
            skips (int, optional): The number of letters that can be skipped. Default is 0.

        Returns:
            tuple: A tuple containing the path of letters forming the word, its value, and skipped letters.

        Checks if the board contains the specified word considering skips and multipliers.
        """
        row_count, column_count = self.row_count, self.column_count
        if not skips and not self.precheck(word):
            return [], 0, []

        def backtrack(starting_row, starting_column, remaining_letters):
            if not remaining_letters:
                return True
            if self.board[starting_row][starting_column] != remaining_letters[0]:
                if self.skips and self.board[starting_row][starting_column] != ".":
                    self.skips -= 1
                else:
                    return False

            temp, self.board[starting_row][starting_column] = self.board[starting_row][starting_column], "."
            end_loop = False
            if starting_row + 1 < row_count:
                end_loop = end_loop or backtrack(starting_row + 1, starting_column, remaining_letters[1:])
                if starting_column + 1 < column_count:
                    end_loop = end_loop or backtrack(starting_row + 1, starting_column + 1, remaining_letters[1:])
                if starting_column > 0:
                    end_loop = end_loop or backtrack(starting_row + 1, starting_column - 1, remaining_letters[1:])
            if starting_row > 0:
                end_loop = end_loop or backtrack(starting_row - 1, starting_column, remaining_letters[1:])
                if starting_column + 1 < column_count:
                    end_loop = end_loop or backtrack(starting_row - 1, starting_column + 1, remaining_letters[1:])
                if starting_column > 0:
                    end_loop = end_loop or backtrack(starting_row - 1, starting_column - 1, remaining_letters[1:])
            if starting_column + 1 < column_count:
                end_loop = end_loop or backtrack(starting_row, starting_column + 1, remaining_letters[1:])
            if starting_column > 0:
                end_loop = end_loop or backtrack(starting_row, starting_column - 1, remaining_letters[1:])

            self.board[starting_row][starting_column] = temp
            if self.board[starting_row][starting_column] != remaining_letters[0]:
                self.skips += 1

            if end_loop:
                path.append((starting_row, starting_column))
                if self.board[starting_row][starting_column] != remaining_letters[0]:
                    skipped.append((starting_row, starting_column))
            return end_loop

        best = 0
        out = ([], 0, [])
        for row in range(row_count):
            for column in range(column_count):
                self.skips = skips
                path = []
                skipped = []
                if self.board[row][column] == word:
                    value = (
                            self.letter_multipliers[(row, column)]
                            * self.word_multipliers[(row, column)]
                            * LETTERS_AND_VALUES[word[0].lower()]
                    )
                    if value > best:
                        out = ([(row, column)], value, [])
                        best = value
                if self.board[row][column] == word[0]:
                    if backtrack(row, column, word):
                        word_multiplier = reduce(
                            lambda accumulator, current: accumulator * self.word_multipliers[current],
                            path,
                            1,
                        )
                        value = (
                                sum(
                                    self.letter_multipliers[cell]
                                    * LETTERS_AND_VALUES[word[letter_index].lower()]
                                    for letter_index, cell in enumerate(path[::-1])
                                )
                                * word_multiplier
                        )
                        if value > best:
                            out = (path, value, skipped)
                            best = value
        return out

    def best_word(self, skips=0):
        """
        Find the best word that can be formed on the board.

        Args:
            skips (int, optional): The number of letters that can be skipped. Default is 0.

        Returns:
            tuple: A tuple containing the best word, its value, path, and skipped letters.

        Finds the highest scoring word that can be formed on the board, considering skips and multipliers.
        """
        current_best = ("", 0, [], [])
        current_value = 0
        for _, word in self.word_values:
            path, actual_value, skipped = self.board_contains(word, skips)
            if path and actual_value > current_value:
                current_value = actual_value
                current_best = (word, actual_value, path, skipped)
        return current_best

    def add_multiplier(self, row, column, multiplier, word):
        """
        Add a multiplier to a specific cell on the board.

        Args:
            row (int): The row of the cell to which the multiplier is applied.
            column (int): The column of the cell to which the multiplier is applied.
            multiplier (int): The multiplier value to be added.
            word (bool): True if the multiplier is for a word, False if it's for a letter.

        Updates multipliers and recalculates attributes based on the new multiplier.
        """
        if word:
            self.word_multipliers[(row, column)] = multiplier
        else:
            self.letter_multipliers[(row, column)] = multiplier
        self.recalculate()

    def remove_multiplier(self, row, column):
        """
        Remove multipliers from a specific cell on the board.

        Args:
            row (int): The row of the cell from which the multipliers are removed.
            column (int): The column of the cell from which the multipliers are removed.

        Resets multipliers for the specified cell and recalculates attributes.
        """
        self.word_multipliers[(row, column)] = 1
        self.letter_multipliers[(row, column)] = 1
        self.recalculate()


if __name__ == "__main__":
    # Read board and create wordboard
    board = [[character.lower() for character in input()] for _ in range(5)]
    word_board = WordBoard()
    word_board.set_board(board)
    def findBestWords():
        # Find best words
        best_word_with_no_swaps = word_board.best_word()  # no swaps
        print("No swaps:\n", best_word_with_no_swaps)
        best_word_with_one_swap = word_board.best_word(1)  # one swap
        print("One swap:\n", best_word_with_one_swap)
        best_word_with_two_swaps = word_board.best_word(2)  # two swaps
        print("Two swaps:\n", best_word_with_two_swaps)
    
    threading.Thread(target=findBestWords).start()

    #x, y = map(int, input().split())
    #wgXY = word_board.generateWords(x=x, y=y)