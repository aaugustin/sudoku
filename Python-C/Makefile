# Makefile for sudoku
# Copyright (c) 2009 Aymeric Augustin

build: csudoku.c csudoku.h
	python setup.py build
	ln -snf build/lib.*/csudoku.so .

debug: csudoku.c csudoku.h
	python setup.py build --debug
	ln -snf build/lib.*/csudoku.so .

install: build
	python setup.py install

dist:
	python setup.py sdist

clean:
	python setup.py clean
	rm -rf build
	rm -rf dist
	rm -f csudoku.so
	rm -f *.pyc

test: build
	nosetests test_*.py

test-cover: build
	nosetests --with-coverage --cover-inclusive --cover-erase test_*.py
