import tkinter as tk
import tkinter.font as tkFont
from spellcast import *


class App:
    def __init__(self, root):
        self.wb = WordBoard()

        root.title("Spellcast Word Finder")
        width = 600
        height = 256
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        alignstr = "%dx%d+%d+%d" % (
            width,
            height,
            (screenwidth - width) / 2,
            (screenheight - height) / 2,
        )
        root.geometry(alignstr)
        root.resizable(width=False, height=False)

        self.vals = [
            [tk.StringVar(root, value="") for __ in range(5)] for _ in range(5)
        ]
        self.lineInput = []
        self.labels = []

        def on_validate(p, i, j):
            i, j = map(int, (i, j))
            ind = (i * 5 + j + 1) % 25
            if len(p) == 1:
                self.lineInput[ind].focus_set()
                self.lineInput[ind].select_range(0, "end")
            return True

        xoff, yoff = 25, 25
        for i in range(5):
            for j in range(5):
                self.lineInput += [
                    tk.Entry(
                        root,
                        textvariable=self.vals[i][j],
                        validate="key",
                        highlightthickness=2,
                    )
                ]
                self.lineInput[-1]["borderwidth"] = "1px"
                self.lineInput[-1]["font"] = tkFont.Font(family="Times", size=10)
                self.lineInput[-1]["fg"] = "#333333"
                self.lineInput[-1]["justify"] = "center"
                self.lineInput[-1]["validatecommand"] = (
                    self.lineInput[-1].register(on_validate),
                    "%P",
                    i,
                    j,
                )
                self.lineInput[-1].place(
                    x=xoff + j * 32, y=yoff + i * 32, width=32, height=32
                )
                self.lineInput[-1].configure(
                    highlightbackground="black",
                    highlightcolor="black",
                    font=("Roboto", 16),
                )

        for i in range(3):
            self.labels += [tk.Label(root)]
            self.labels[-1]["font"] = tkFont.Font(family="Times", size=10)
            self.labels[-1]["fg"] = "#333333"
            self.labels[-1]["justify"] = "center"
            self.labels[-1]["text"] = f""
            self.labels[-1].place(x=320, y=80 + i * 30, width=250, height=25)

        self.button = tk.Button(root)
        self.button["bg"] = "#e9e9ed"
        self.button["font"] = tkFont.Font(family="Times", size=10)
        self.button["fg"] = "#000000"
        self.button["justify"] = "center"
        self.button["text"] = "Generate Words"
        self.button.place(x=xoff, y=yoff + 160, width=160, height=25)
        self.button["command"] = self.button_command

    class lblHover:
        def __init__(self, label, path, skipped, lineInput, vals, word):
            self.label = label
            self.path = path
            self.skipped = skipped
            self.skipset = set(skipped)
            self.lineInput = lineInput
            self.label.bind("<Enter>", lambda _: self.hover())
            self.label.bind("<Leave>", lambda _: self.unhover())
            self.vals = vals
            self.temp = [[v.get().lower() for v in line] for line in self.vals]
            self.word = word

        def hover(self):
            for (i, j), c in zip(self.path[::-1], self.word):
                self.lineInput[i * 5 + j].configure(
                    highlightbackground="blue",
                    highlightcolor="blue",
                    background="blue",
                    font=("Roboto", 20, tk.font.BOLD),
                    fg="white",
                )
                if (i, j) in self.skipset:
                    self.vals[i][j].set(c)

            for i, j in self.skipped:
                self.lineInput[i * 5 + j].configure(
                    highlightbackground="red",
                    highlightcolor="red",
                    background="red",
                    font=("Roboto", 20, tk.font.BOLD),
                    fg="white",
                )

        def unhover(self):
            for i, j in self.path + self.skipped:
                self.lineInput[i * 5 + j].configure(
                    highlightbackground="black",
                    highlightcolor="black",
                    background="white",
                    font=("Roboto", 16, tk.font.NORMAL),
                    fg="black",
                )
                self.vals[i][j].set(self.temp[i][j])

    def button_command(self):
        board = [[v.get().lower() for v in line] for line in self.vals]
        self.wb.setBoard(board)

        words = [
            self.wb.bestWord(i) for i in range(3)  # (best word, value, path, skipped)
        ]

        wordLabelPrefix = ["No swaps", "One swap", "Two swaps"]

        for i, word in enumerate(words):
            self.labels[i]["text"] = f"{wordLabelPrefix[i]}: {word[:2]}"
            self.lblHover(
                self.labels[i], word[2], word[3], self.lineInput, self.vals, word[0]
            )

    """
		TODO implement
			should allow user to input multiplier amount and cell
			should update spellcast board to account for multiplier
	"""

    def addMultiplier(self, i, j, word=False):
        self.wb.addMultiplier(i, j, 1)

    def removeMultiplier(self, i, j):
        self.wb.removeMultiplier(i, j)


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
