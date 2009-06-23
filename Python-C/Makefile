# Makefile for sudoku
# Copyright (c) 2009 Aymeric Augustin

# Avoid copying the resource forks when tar-ing on Mac OS X 10.5
export COPYFILE_DISABLE=true

build: sudoku/csudoku.c sudoku/csudoku.h
	python setup.py build
	cd sudoku && ln -snf ../build/lib.*/sudoku/csudoku.so .

debug: sudoku/csudoku.c sudoku/csudoku.h
	python setup.py build --debug
	cd sudoku && ln -snf ../build/lib.*/sudoku/csudoku.so .

install: build setup.py
	python setup.py install

dist: setup.py MANIFEST.in
	python setup.py sdist --force-manifest

clean:
	python setup.py clean
	rm -rf build
	rm -rf dist
	rm -f MANIFEST
	rm -f sudoku/*.pyc
	rm -f sudoku/csudoku.so

.PHONY: test
test: debug
	python test/test_sudoku.py
	python test/test_executable.py

.PHONY: test-cover
test-cover: debug
	nosetests --with-coverage --cover-inclusive --cover-erase test/test_sudoku.py
