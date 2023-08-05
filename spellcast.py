from collections import Counter, defaultdict
from functools import reduce
from itertools import product

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
    def __init__(self):
        with open("words.txt", encoding="utf-8") as file:
            self.words = [word[:-1] for word in file.readlines()]

    def recalculate(self):
        max_global_multiplier = max(self.word_multipliers.values(), default=1)
        max_character_multiplier = defaultdict(lambda: 1)
        for row, column in product(range(5), range(5)):
            max_character_multiplier[self.board[row][column]] = max(
                max_character_multiplier[self.board[row][column]],
                max_global_multiplier,
                self.letter_multipliers[(row, column)],
            )

        self.letter_values = {
            letter: val * max_character_multiplier[letter]
            for letter, val in LETTERS_AND_VALUES.items()
        }
        self.board_value = {}
        for row, column in product(range(5), range(5)):
            self.board_value[(row, column)] = self.letter_values[
                self.board[row][column].lower()
            ]

        self.calculate_value = lambda word: sum(
            self.letter_values[character.lower()]
            for character in word
            if character.lower() in LETTERS_AND_VALUES
        ) + (10 if len(word) > 6 else 0)

        self.word_values = [(self.calculate_value(word), word) for word in self.words]
        self.word_values.sort(reverse=True)

    def set_board(self, board):
        self.board = board
        self.row_count = len(board)
        self.column_count = len(board[0])
        self.total_count = Counter(cell for row in board for cell in row)

        self.word_multipliers = defaultdict(lambda: 1)
        self.letter_multipliers = defaultdict(lambda: 1)
        self.recalculate()

    def precheck(self, word):
        word_count = Counter(word)
        for character in word_count:
            if word_count[character] > self.total_count[character]:
                return False
        return True

    def board_contains(self, word, skips=0):
        row_count, column_count = self.row_count, self.column_count
        if not skips and not self.precheck(word):
            return ([], 0, [])

        def backtrack(row, column, remaining_letters):
            if not remaining_letters:
                return True
            if self.board[row][column] != remaining_letters[0]:
                if self.skips and self.board[row][column] != ".":
                    self.skips -= 1
                else:
                    return False

            temp, self.board[row][column] = self.board[row][column], "."
            out = False
            if row + 1 < row_count:
                out = out or backtrack(row + 1, column, remaining_letters[1:])
                if column + 1 < column_count:
                    out = out or backtrack(row + 1, column + 1, remaining_letters[1:])
                if column > 0:
                    out = out or backtrack(row + 1, column - 1, remaining_letters[1:])
            if row > 0:
                out = out or backtrack(row - 1, column, remaining_letters[1:])
                if column + 1 < column_count:
                    out = out or backtrack(row - 1, column + 1, remaining_letters[1:])
                if column > 0:
                    out = out or backtrack(row - 1, column - 1, remaining_letters[1:])
            if column + 1 < column_count:
                out = out or backtrack(row, column + 1, remaining_letters[1:])
            if column > 0:
                out = out or backtrack(row, column - 1, remaining_letters[1:])

            self.board[row][column] = temp
            if self.board[row][column] != remaining_letters[0]:
                self.skips += 1

            if out:
                path.append((row, column))
                if self.board[row][column] != remaining_letters[0]:
                    skipped.append((row, column))
            return out

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
                            lambda accumulator, current: accumulator
                            * self.word_multipliers[current],
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
        current_best = ("", 0, [], [])
        current_value = 0
        for _, word in self.word_values:
            path, actual_value, skipped = self.board_contains(word, skips)
            if path and actual_value > current_value:
                current_value = actual_value
                current_best = (word, actual_value, path, skipped)
        return current_best

    def add_multiplier(self, row, column, multiplier, word):
        if word:
            self.word_multipliers[(row, column)] = multiplier
        else:
            self.letter_multipliers[(row, column)] = multiplier
        self.recalculate()

    def remove_multiplier(self, i, j):
        self.word_multipliers[(i, j)] = 1
        self.letter_multipliers[(i, j)] = 1
        self.recalculate()


if __name__ == "__main__":
    # Read board and create wordboard
    board = [[character.lower() for character in input()] for _ in range(5)]
    word_board = WordBoard()
    word_board.set_board(board)

    # Find best words
    best_word_with_no_swaps = word_board.best_word()  # no swaps
    best_word_with_one_swap = word_board.best_word(1)  # one swap
    best_word_with_two_swaps = word_board.best_word(2)  # two swaps

    # x, y = map(int, input().split())
    # wgXY = wb.generateWords(x=x, y=y)

    print("No swaps:", best_word_with_no_swaps)
    print("One swap:", best_word_with_one_swap)
    print("Two swaps:", best_word_with_two_swaps)
