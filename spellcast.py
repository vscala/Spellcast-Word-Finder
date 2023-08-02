from collections import Counter, defaultdict
from functools import reduce
from itertools import chain, product

LETTERS_AND_VALUES = {
    "a": 1, "b": 4, "c": 5, "d": 3, "e": 1, "f": 5, "g": 3, "h": 4,
    "i": 1, "j": 7, "k": 3, "l": 3, "m": 4, "n": 2, "o": 1, "p": 4,
    "q": 8, "r": 2, "s": 2, "t": 2, "u": 4, "v": 5, "w": 5, "x": 7,
    "y": 4, "z": 8,
}

class WordBoard:
    def __init__(self):
        with open("words.txt", encoding="utf-8") as f:
            self.words = [word[:-1] for word in f.readlines()]

    def recalculate(self):
        maxGlobalMultiplier = max(self.wordMultipliers.values(), default=1)
        maxCharMultiplier = defaultdict(lambda: 1)
        for i, j in product(range(5), range(5)):
            maxCharMultiplier[self.board[i][j]] = max(
                maxCharMultiplier[self.board[i][j]],
                maxGlobalMultiplier,
                self.letterMultipliers[(i, j)],
            )

        self.letterVals = {
            letter: val * maxCharMultiplier[letter] for letter, val in LETTERS_AND_VALUES.items()
        }
        self.boardValue = {}
        for i, j in product(range(5), range(5)):
            self.boardValue[(i, j)] = self.letterVals[self.board[i][j].lower()]

        self.value = lambda word: sum(
            self.letterVals[c.lower()] for c in word if c.lower() in LETTERS_AND_VALUES
        ) + (10 if len(word) > 6 else 0)

        self.wordValues = [(self.value(word), word) for word in self.words]
        self.wordValues.sort(reverse=True)

    def setBoard(self, board):
        self.board = board
        self.n = len(board)
        self.m = len(board[0])
        self.totalCount = Counter(chain(*board))

        self.wordMultipliers = defaultdict(lambda: 1)  # word multiplier at (i, j)
        self.letterMultipliers = defaultdict(lambda: 1)  # letter multiplier at (i, j)
        self.recalculate()

    def precheck(self, word):
        wCount = Counter(word)
        for c in wCount:
            if wCount[c] > self.totalCount[c]:
                return False
        return True

    # returns (path, actualValue, skipped)
    def boardContains(self, word, skips=0):
        n, m = self.n, self.m
        if not skips and not self.precheck(word):
            return ([], 0, [])

        def backtrack(i, j, letters):
            if not letters:
                return True
            if self.board[i][j] != letters[0]:
                if self.skips and self.board[i][j] != ".":
                    self.skips -= 1
                else:
                    return False

            temp, self.board[i][j] = self.board[i][j], "."
            out = False
            if i + 1 < n:
                out = out or backtrack(i + 1, j, letters[1:])  # +1, 0
                if j + 1 < m:
                    out = out or backtrack(i + 1, j + 1, letters[1:])  # +1, +1
                if j > 0:
                    out = out or backtrack(i + 1, j - 1, letters[1:])  # +1, -1
            if i > 0:
                out = out or backtrack(i - 1, j, letters[1:])  # -1, 0
                if j + 1 < m:
                    out = out or backtrack(i - 1, j + 1, letters[1:])  # -1, +1
                if j > 0:
                    out = out or backtrack(i - 1, j - 1, letters[1:])  # -1, -1
            if j + 1 < m:
                out = out or backtrack(i, j + 1, letters[1:])  # 0, +1
            if j > 0:
                out = out or backtrack(i, j - 1, letters[1:])  # 0, -1

            # reset board values
            self.board[i][j] = temp
            if self.board[i][j] != letters[0]:
                self.skips += 1

            # if path found update path, skipped
            if out:
                path.append((i, j))
                if self.board[i][j] != letters[0]:
                    skipped.append((i, j))
            return out

        best = 0
        out = ([], 0, [])
        # Iterate over all starting positions
        for i in range(n):
            for j in range(m):
                self.skips = skips
                path = []
                skipped = []
                # Singleton words
                if self.board[i][j] == word:
                    value = (
                        self.letterMultipliers[(i, j)]
                        * self.wordMultipliers[(i, j)]
                        * LETTERS_AND_VALUES[word[0].lower()]
                    )
                    if value > best:
                        out = ([(i, j)], value, [])
                        best = value
                # Non-singleton words
                if self.board[i][j] == word[0]:
                    if backtrack(i, j, word):
                        wordMultiplier = reduce(
                            lambda acc, cur: acc * self.wordMultipliers[cur], path, 1
                        )
                        value = (
                            sum(
                                self.letterMultipliers[x] * LETTERS_AND_VALUES[word[ind].lower()]
                                for ind, x in enumerate(path[::-1])
                            )
                            * wordMultiplier
                        )
                        if value > best:
                            out = (path, value, skipped)
                            best = value
        return out

    # returns (best word, value, path, skipped)
    def bestWord(self, skips=0):
        curBest = ("", 0, [], [])
        curVal = 0
        for _, word in self.wordValues:
            path, actualValue, skipped = self.boardContains(word, skips)
            if path and actualValue > curVal:
                curVal = actualValue
                curBest = (word, actualValue, path, skipped)
        return curBest

    def addMultiplier(self, i, j, m, word):
        if word:
            self.wordMultipliers[(i, j)] = m
        else:
            self.letterMultipliers[(i, j)] = m
        self.recalculate()

    def removeMultiplier(self, i, j):
        self.wordMultipliers[(i, j)] = 1
        self.letterMultipliers[(i, j)] = 1
        self.recalculate()


if __name__ == "__main__":
    # Read board and create wordboard
    board = [[c.lower() for c in input()] for _ in range(5)]
    wb = WordBoard()
    wb.setBoard(board)

    # Find best words
    wg = wb.bestWord()  # no swaps
    wgS1 = wb.bestWord(1)  # one swap
    wgS2 = wb.bestWord(2)  # two swaps

    # x, y = map(int, input().split())
    # wgXY = wb.generateWords(x=x, y=y)

    print("No swaps:", (wg))
    print("One swap:", (wgS1))
    print("Two swaps:", (wgS2))
