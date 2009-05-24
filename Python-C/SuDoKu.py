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
from csudoku import CSuDoKu, Contradiction, MultipleSolutionsFound

class InputError(Exception):
	pass

class UsageError(Exception):
	pass

class SuDoKu(CSuDoKu):
	
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
