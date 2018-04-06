import os
import numpy as np
import scipy.signal


class Connect4Environment(object):
	"""A class that wraps around the Connect4 game engine to accomodate a RL agent"""

	def __init__(self):

		self.game = Connect4()

	def get_state(self):
		"""Transform matrix grid representation into a 3D state of one-hot vectors (n_rows x n_columns x 3)"""
		pass

	def step(self, action):
		"""Makes a move in the environment that leads to a reward and a next state"""

		next_state = self.game.make_move(action, imaginary=False) # the state of the world is effectively modified
		reward = int(self.game.check_win(1))

		return next_state, reward

	def get_successors(self):
		"""Returns a list of tuples containing afterstates and actions that leads to those afterstates"""

		afterstates = [] # list of tuples (successor, action)
		valid_actions = self.game.get_valid_moves()
		
		for action in valid_actions:
			successor = self.game.make_move(action, imaginary=True) # the state of the world won't be modified (here we only simulate)
			successor_state = self.get_state(successor)
			afterstates.append((successor_state, action))

		return afterstates

	def reset():
		"""Resets the environment"""
		self.game.reset()

	def render():
		pass


class Connect4(object):
	"""Our game engine"""

	def __init__(self, n_rows=6, n_columns=7, win_streak=4):

		self.n_rows = n_rows
		self.n_columns = n_columns
		self.win_streak = win_streak
		self.grid = np.zeros(shape=(n_rows, n_columns))

		# Creates kernels to check the different winning conditions
		h_win_kernel = np.ones(shape=(1, win_streak)) # horizontal win
		v_win_kernel = np.ones(shape=(win_streak, 1)) # vertical win
		d1_win_kernel = np.zeros(shape=(win_streak, win_streak)) # diagonal-1 win
		d2_win_kernel = np.zeros(shape=(win_streak, win_streak)) # diagonal-2 win
		for i in range(win_streak):
			d1_win_kernel[i,i] = 1
			d2_win_kernel[i, win_streak-i-1] = 1
		self.win_kernels = [h_win_kernel, v_win_kernel, d1_win_kernel, d2_win_kernel]

	def make_move(self, player_id, column, imaginary=False):
		"""Places a piece of the player's color in the given column"""

		# Initializes next grid to current state of the game
		next_grid = self.grid

		# Checks if the column is full (should not happen)
		if self.grid[0, column] != 0:
			raise ValueError('This move is illegal. Column {} is already full.'.format(column))

		for row in range(self.n_rows):
			# If next row is empty
			if row+1 < self.n_rows and self.grid[row+1, column] == 0:
				continue # Piece keeps falling
			else:
				next_grid[row, column] = player_id
				break # Piece stops here

		if not imaginary:
			self.grid = next_grid

		return next_grid

	def get_valid_moves(self):
		"""Returns a list of columns in which it is possible to place an additional piece"""

		valid_columns = []
		# Checks for every column if we could add at least on additional piece
		for column in range(self.n_columns):
			if self.grid[0, column] == 0:
				valid_columns.append(column)

		return valid_columns
	
	def check_win(self, player_id):
		"""Checks if the provided player has won the game"""

		# Only keeps the position of the player's pieces we are concerned with
		player_pieces = (self.grid == player_id)
		for kernel in self.win_kernels:

			# Convolves the grid with the wining condition kernels
			win_mask = scipy.signal.convolve2d(player_pieces, kernel, mode="full")
			has_won = np.any(win_mask >= self.win_streak)
			
			if has_won:
				break

		return has_won

	def reset(self):
		self.grid = np.zeros(shape=(self.n_rows, self.n_columns))

	def print_grid(self):
		top = '_' * (self.n_columns+2)
		print(top)
		for i in range(self.n_rows):
			row = '|'
			for j in range(self.n_columns):
				if self.grid[i,j] == 0:
					row += ' '
				elif self.grid[i,j] == 1:
					row += '\u25CF'
				elif self.grid[i,j] == 2:
					row += '\u25CB'
				else:
					raise ValueError("Irregular value in 'self.grid' : {}".format(self.grid))
			print(row + '|')
		bottom = '\u2588' * (self.n_columns+2) # '\u203E'
		print(bottom)
		print(' 0123456 ')
		print("\n")


if __name__ == "__main__":

	game = Connect4()

	while 1:

		# Player moves
		A_s = game.get_valid_moves()
		print("Valid moves : {}".format(A_s))
		a = int(input("Your move : "))
		game.make_move(1, a)
		game.print_grid()

		if game.check_win(1):
			print("Congratulations! You have won!")
			break

		# Random move from opponent
		A_s = game.get_valid_moves()
		a_id = np.random.randint(len(A_s))
		game.make_move(2, A_s[a_id])
		game.print_grid()

		if game.check_win(2):
			print("Player 2 have won. You got beaten by a random bot...")
			break

	print("GAME OVER")


