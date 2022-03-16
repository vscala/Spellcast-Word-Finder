# SpellCast

from collections import defaultdict, Counter
from itertools import chain

letter_values = [1, 4, 5, 3, 1, 5, 3, 4, 1, 7, 3, 3, 4, 2, 1, 4, 8, 2, 2, 2, 4, 5, 5, 7, 4, 8] 
charset = set('abcdefghijklmnopqrstuvwxyz')
value = lambda word : sum(letter_values[ord(c.lower()) - ord('a')] for c in word if c.lower() in charset) + (20 if len(word) > 6 else 0)

class WordBoard:
	def __init__(self):
		with open('words.txt') as f:
			self.words = [word[:-1] for word in f.readlines()]
		self.word_values = [(value(word), word) for word in self.words]
		self.word_values.sort(reverse=True)
		
		
	def setBoard(self, board):
		self.board = board
		self.n = len(board)
		self.m = len(board[0])
		self.totalCount = Counter(chain(*board))
	
	def precheck(self, word):
		wCount = Counter(word)
		for c in wCount:
			if wCount[c] > self.totalCount[c]: return False
		return True
	
	'''
		word: the word to check if the board contains
		skips: the number of letters in the word that can be skipped (TODO)
		x, y: the position of a letter that must be included (None if no such letter exsist)
		
		return (the word path, value delta, and swap positions) # TODO
	'''
	def boardContains(self, word, skips=0, x=None, y=None) -> bool:
		n, m = self.n, self.m
		if not skips and not self.precheck(word):
			return False
		self.hitXY = (x == None)
		self.skips = skips
		
		def backtrack(i, j, letters):
			if not letters: return True
			if self.board[i][j] != letters[0]: 
				if self.skips and self.board[i][j] != '.': self.skips -= 1
				else: return False
			if i == x and j == y:
				self.hitXY = True
			
			temp, self.board[i][j] = self.board[i][j], "."
			out = False
			if i+1 < n: 
				out = out or backtrack(i+1, j, letters[1:]) 		# +1, 0
				if j+1 < m:
					out = out or backtrack(i+1, j+1, letters[1:]) 	# +1, +1
				if j > 0:
					out = out or backtrack(i+1, j-1, letters[1:])	# +1, -1
			if i > 0: 
				out = out or backtrack(i-1, j, letters[1:]) 		# -1, 0
				if j+1 < m:
					out = out or backtrack(i-1, j+1, letters[1:]) 	# -1, +1
				if j > 0:
					out = out or backtrack(i-1, j-1, letters[1:])	# -1, -1
			if j+1 < m: 
				out = out or backtrack(i, j+1, letters[1:]) 		# 0, +1
			if j > 0: 
				out = out or backtrack(i, j-1, letters[1:])		# 0, -1
			out = out and self.hitXY
			
			# reset board values
			self.board[i][j] = temp
			if self.board[i][j] != letters[0]: 
				self.skips += 1
			if i == x and j == y:
				self.hitXY = False
			return out
	   	
		#Iterate over board
		for i in range(n):
			for j in range(m):
				if self.board[i][j] == word: return True
				if self.board[i][j] == word[0]:
					if backtrack(i, j, word):
						return True   
	
	def generateWords(self, skips=0, x=None, y=None):
		for value, word in self.word_values:
			cur = self.boardContains(word, skips, x, y)
			if cur:
				yield (word, value, cur)

if __name__ == "__main__":
	# Read board and create wordboard
	board = [[c.lower() for c in input()] for _ in range(5)]
	wb = WordBoard()
	wb.setBoard(board)

	# Find best words
	wg = wb.generateWords()		# no swaps
	wgS1 = wb.generateWords(1)	# one swap
	wgS2 = wb.generateWords(2)	# two swaps

	#x, y = map(int, input().split())
	#wgXY = wb.generateWords(x=x, y=y)

	print("No swaps:", next(wg))
	print("One swap:", next(wgS1))
	print("Two swaps:", next(wgS2))



