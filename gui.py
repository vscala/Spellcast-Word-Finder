import tkinter as tk
import tkinter.font as tkFont
from spellcast import *

class App:
	def __init__(self, root):
		self.wb = WordBoard()
		
		root.title("Spellcast Word Finder")
		width=600
		height=256
		screenwidth = root.winfo_screenwidth()
		screenheight = root.winfo_screenheight()
		alignstr = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
		root.geometry(alignstr)
		root.resizable(width=False, height=False)
		
		self.vals = [[tk.StringVar(root, value='') for __ in range(5)] for _ in range(5)]
		self.lineInput = []
		self.labels = []
		
		def on_validate(p, i, j):
			i, j = map(int, (i, j))
			ind = (i * 5 + j + 1) % 25
			if len(p) == 1:
				self.lineInput[ind].focus_set()
				self.lineInput[ind].select_range(0, 'end')
			return True
		
		xoff, yoff = 25, 25
		for i in range(5):
			for j in range(5):
				self.lineInput += [tk.Entry(root, textvariable=self.vals[i][j], validate="key")]
				self.lineInput[-1]["borderwidth"] = "1px"
				self.lineInput[-1]["font"] = tkFont.Font(family='Times',size=10)
				self.lineInput[-1]["fg"] = "#333333"
				self.lineInput[-1]["justify"] = "center"
				self.lineInput[-1]['validatecommand'] = (self.lineInput[-1].register(on_validate), '%P', i, j)
				self.lineInput[-1].place(x=xoff+j*32,y=yoff+i*32,width=32,height=32)

		for i in range(3):
			self.labels += [tk.Label(root)]
			self.labels[-1]["font"] = tkFont.Font(family='Times',size=10)
			self.labels[-1]["fg"] = "#333333"
			self.labels[-1]["justify"] = "center"
			self.labels[-1]["text"] = f""
			self.labels[-1].place(x=320,y=80+i*30,width=250,height=25)

		self.button = tk.Button(root)
		self.button["bg"] = "#e9e9ed"
		self.button["font"] = tkFont.Font(family='Times',size=10)
		self.button["fg"] = "#000000"
		self.button["justify"] = "center"
		self.button["text"] = "Generate Words"
		self.button.place(x=xoff,y=yoff+160,width=160,height=25)
		self.button["command"] = self.button_command

	def button_command(self):
		board = [[v.get().lower() for v in line] for line in self.vals]
		self.wb.setBoard(board)

		wg = self.wb.generateWords()
		wgS1 = self.wb.generateWords(1)	
		wgS2 = self.wb.generateWords(2)
		
		self.labels[0]["text"] = f"No swaps: {next(wg)}"
		self.labels[1]["text"] = f"One swap: {next(wgS1)}"
		self.labels[2]["text"] = f"Two swaps: {next(wgS2)}"
		

if __name__ == "__main__":
	root = tk.Tk()
	app = App(root)
	root.mainloop()

