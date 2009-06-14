# Makefile for sudoku
# Copyright (c) 2009 Aymeric Augustin

build:
	python setup.py build
	ln -s build/lib.*/csudoku.so .

install:
	python setup.py install

dist:
	python setup.py sdist

clean:
	python setup.py clean
	rm csudoku.so
	rm *.pyc

test:
	nosetests test_*.py

test-cover:
	nosetests --with-coverage --cover-inclusive --cover-erase test_*.py
