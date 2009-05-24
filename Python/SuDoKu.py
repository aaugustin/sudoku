#!/usr/bin/env python

# SuDoKu generator and solver
# 
# Copyright (C) 2008 Aymeric Augustin
# 
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA  02111-1307, USA.


import copy, random, sys
from math import log
from optparse import OptionParser

class InputError(Exception):
	pass

class UsageError(Exception):
	pass

class Contradiction(Exception):
	pass

class MultipleSolutionsFound(Exception):
	pass

class SuDoKu:
	
	# precompute relation map
	relations = [[[(k, l) for k in range(9) for l in range(9) if (k == i or l == j or (k // 3 == i // 3 and l // 3 == j // 3)) and not (k == i and l == j)] for j in range(9)] for i in range(9)]
	
	def __init__(self, debug=False):
		# initial values: 1..9 or 0 = undefined
		self.o = [[0 for j in range(9)] for i in range(9)]
		# set to true to enable verbose debugging
		self.d = debug
	
	def debug(self, msg):
		if self.d:
			print msg
	
	def reset(self):
		# Resolution
		# 
		# computed values: 1..9 or 0 = undefined
		self.v = [[0 for j in range(9)] for i in range(9)]
		# possible values at each position: subset of 1..9
		self.p = [[range(1, 10) for j in range(9)] for i in range(9)]
		# queue of positions for which the value is determined
		self.q = []
		
		# Statistics
		# 
		# number of known values
		self.n = 0
		# graph of resolution paths
		self.g = None
	
	# Resolution functions
	#---------------------
	
	def markInput(self, i, j, n):
		self.o[i][j] = n
	
	def mark(self, i, j, n):
		# Ignore if the position is already marked
		# This allows redundancy in the problems
		if self.v[i][j] == n:
			return
		# Check that the value is possible
		if self.p[i][j].count(n) == 0:
			self.debug('    Attempt to assign %d at (%d, %d) which is forbidden' % (n, i, j))
			self.g = (self.n, '-')
			raise Contradiction
		# Record the value
		self.v[i][j] = n
		self.n += 1
		# Prevent detection of a contradiction at this position
		self.p[i][j] = []
		# Apply rules
		for (k, l) in SuDoKu.relations[i][j]:
			self.eliminate(k, l, n)
		# Apply recursively
		if len(self.q) > 0:
			i, j, n = self.q.pop(0)
			self.mark(i, j, n)
	
	def eliminate(self, i, j, n):
		# Remove the element from the list of possible values
		try:
			self.p[i][j].remove(n)
		except ValueError:
			return
		# This is executed only when an element has actually been 
		# removed from the list, e.g. no more than once for a value of
		# len(self.p[i][j])
		# 
		# If there's no possible value, we are on a wrong branch
		if len(self.p[i][j]) == 0:
			self.debug('    Impossibility at (%d, %d), search depth = %d' % (i, j, self.n))
			self.g = (self.n, '-')
			raise Contradiction
		# If there's one possible value, we mark it
		elif len(self.p[i][j]) == 1:
			self.q.append((i, j, self.p[i][j][0]))
	
	def searchMin(self):
		im = jm = -1
		lm = 10
		for i in range(9):
			for j in range(9):
				if self.v[i][j] == 0 and len(self.p[i][j]) < lm:
					im = i
					jm = j
					lm = len(self.p[i][j])
		return im, jm
	
	def resolveAux(self):
		# If the grid is complete
		if self.n == 81:
			self.debug('    Found a solution: %s' % self.toString())
			self.g = (self.n, '+')
			return [self.v]
		# Otherwise look for the position that has the least alternatives
		i, j = self.searchMin()
		# Try each alternative
		r = []
		self.g = (self.n, [])
		for n in self.p[i][j]:
			self.debug('Trying %d at (%d, %d), search depth = %d' % (n, i, j, self.n))
			t = copy.deepcopy(self)
			try:
				t.mark(i, j, n)
			except Contradiction:
				self.g[1].append(t.g)
				continue
			r.extend(t.resolveAux())
			self.g[1].append(t.g)
		return r
	
	def resolve(self):
		# Step 0: initialize for resolution
		self.reset()
		
		# Step 1: complete all trivial stuff
		for i in range(9):
			for j in range(9):
				if self.o[i][j] > 0:
					self.mark(i, j, self.o[i][j])
		
		# Step 2: explore different paths
		return self.resolveAux()
	
	# Generation functions
	#---------------------
	
	def uniqueSolAux(self):
		# Based on resolve
		i, j = self.searchMin()
		if i == -1:
			return 1
		else:
			count = 0
			for n in self.p[i][j]:
				t = copy.deepcopy(self)
				try:
					t.mark(i, j, n)
				except Contradiction:
					continue
				count += t.uniqueSolAux()
				if count > 1:
					raise MultipleSolutionsFound
			return count
	
	def uniqueSol(self):
		self.reset()
		for i in range(9):
			for j in range(9):
				if self.o[i][j] > 0:
					self.mark(i, j, self.o[i][j])
		try:
			self.uniqueSolAux()
			return True
		except MultipleSolutionsFound:
			return False
	
	def generate(self):
		# Step 0: initialize for generation
		self.reset()
		
		# Step 1: select an order to fill positions
		self.debug('Shuffling positions...')
		order = [(i, j) for i in range(9) for j in range(9)]
		random.shuffle(order)
		self.debug('    Done.')
		
		# Step 2: generate problem
		self.debug('Generating a random grid...')
		count = 0
		while True:
			try:
				count += 1
				self.reset()
				for i, j in order:
					if self.v[i][j] > 0:
						continue
					else:
						self.mark(i, j, random.choice(self.p[i][j]))
				break
			except Contradiction:
				continue
		self.debug('    Found a grid after %d tries.' % count)
		
		# Step 3: minimize problem
		self.debug('Minimizing problem...')
		for i in range(9):
			for j in range(9):
				self.o[i][j] = self.v[i][j]
		for i, j in order:
			n = self.o[i][j]
			self.o[i][j] = 0
			if self.uniqueSol():
				self.debug('    Removing %d at (%d, %d)' % (n, i, j))
			else:
				self.debug('    Keeping %d at (%d, %d)' % (n, i, j))
				self.o[i][j] = n
		self.debug('    Done.')
	
	# Estimation functions
	#---------------------
	
	def printGraph(self, g, p):
		if isinstance(g[1], list):
			print p + str(g[0]).zfill(2)
			for sg in g[1]:
				self.printGraph(sg, '  ' + p)
		else:
			print p + str(g[0]).zfill(2) + ' ' + g[1]
	
	def graphLen(self, g, d):
		l = g[0] - d
		if isinstance(g[1], list):
			for sg in g[1]:
				l += self.graphLen(sg, g[0])
		return l
	
	def estimate(self):
		# Print resolution graph
		if self.d:
			self.printGraph(self.g, '')
		# Compute "graph length"
		l = self.graphLen(self.g, 0)
		return log(l / 81) + 1
	
	# Input functions
	#----------------
	
	def fromString(self, s):
		i = j = 0
		for c in s:
			if c == '\n' or c == '\r':
				continue
			elif c >= '1' and c <= '9':
				self.markInput(i, j, int(c))
			elif c == '_' or c == '-' or c == ' ' or c == '.' or c == '0':
				pass
			else:
				raise InputError, 'Invalid caracter: %s' % c
			
			if j >= 8:
				j = 0
				i += 1
			else:
				j += 1
		if 9 * i + j < 81:
			raise InputError, 'Bad input: not enough data.'
		elif 9 * i + j > 81:
			raise InputError, 'Bad input: too much data.'
	
	def fromFile(self, f):
		h = open(f)
		self.fromString(h.read())
		h.close()
	
	# Output funtions
	#----------------
	
	def out(self, format='console', mode='both'):
		if format == 'console':
			print self.toConsole(mode)
		elif format == 'html':
			print self.toHTML(mode)
		elif format == 'string':
			print self.toString(mode)
		else:
			raise UsageError, 'Invalid format: %s' % format
	
	def toConsole(self, mode='complete'):
		if mode == 'original':
			values = self.o;
		elif mode == 'complete' or mode == 'both':
			values = self.v;
		else:
			raise UsageError, 'Invalid mode: %s' % mode
		cells = [[str(c) for c in r] for r in values]
		rows = ['| ' + ' | '.join(r) + ' |\n' for r in cells]
		sep = '---'.join([' '] * 10)
		sepnl = sep + '\n'
		return (sepnl + sepnl.join(rows) + sep).replace('0', ' ')
	
	def toHTML(self, mode='complete'):
		if mode == 'original':
			values = self.o;
		elif mode == 'complete' or mode == 'both':
			values = self.v;
		else:
			raise UsageError, 'Invalid mode: %s' % mode
		cells = [['<td>' + str(c) + '</td>' for c in r] for r in values]
		rows = ['<tr>' + ''.join(r) + '</tr>' for r in cells]
		table = '<table class="sudoku">' + ''.join(rows) + '</table>'
		return table.replace('0', '&nbsp;')
	
	def toString(self, mode='complete'):
		if mode == 'original':
			values = self.o;
		elif mode == 'complete' or mode == 'both':
			values = self.v;
		else:
			raise UsageError, 'Invalid mode: %s' % mode
		s =''.join([''.join([str(c) for c in r]) for r in values])
		s = s.replace('0', '_')
		return s


# Main
#-----

if __name__ == '__main__':
	p = OptionParser(usage = 'usage: %prog [options] [problem]')
	# Actions
	p.add_option('-f', '--format',
	             action='store_true', default=False, dest='format',
	             help='Format a problem without resolving it')
	p.add_option('-r', '--resolve',
	             action='store_true', default=False, dest='resolve',
	             help='Resolve a problem (default)')
	p.add_option('-g', '--generate',
	             action='store_true', default=False, dest='generate',
	             help='Generate a problem')
	p.add_option('-e', '--estimate',
	             action='store_true', default=False, dest='estimate',
	             help='Estimate difficulty')
	# Options
	p.add_option('-o', '--output', default='console', dest='output',
	             help='Output format: console (default), html, string')
	p.add_option('-i', '--input', default='', dest='filename', metavar='FILE',
	             help='Read the problem from FILE instead of arguments')
	p.add_option('-d', '--debug',
	             action='store_true', default=False, dest='debug',
	             help='Enable debug (very verbose)')
	(options, args) = p.parse_args()
	
	s = SuDoKu(options.debug)
	
	# Check actions
	if not options.format and not options.resolve and not options.generate:
		options.resolve = True
	
	if (options.format and options.resolve):
		raise UsageError, 'Incompatible options: --format and --resolve.'

	if (options.format and options.generate):
		raise UsageError, 'Incompatible options: --format and --generate.'

	if (options.resolve and options.generate):
		raise UsageError, 'Incompatible options: --resolve and --generate.'
	
	if options.estimate and not (options.resolve or options.generate):
		raise UsageError, '--estimate requires --resolve or --generate.'
	
	# Read problem if necessary
	if options.format or options.resolve:
		if len(args) == 1:
			s.fromString(args[0])
		elif options.filename != '':
			s.fromFile(options.filename)
		else:
			raise UsageError, 'No problem specified.'
	
	if options.format:
		s.out(options.output, 'original')
	
	if options.resolve:
		for grid in s.resolve():
			s.v = grid
			s.out(options.output)
	
	if options.generate:
		s.generate()
		s.out(options.output, 'original')
		
		if options.estimate:
			s.resolve()
	
	if options.estimate:
		print s.estimate()
