# Makefile for sudoku
# Copyright (c) 2009 Aymeric Augustin

# Avoid copying the resource forks when tar-ing on Mac OS X 10.5
export COPYFILE_DISABLE=true

build: csudoku.c csudoku.h
	python setup.py build
	ln -snf build/lib.*/csudoku.so .

debug: csudoku.c csudoku.h
	python setup.py build --debug
	ln -snf build/lib.*/csudoku.so .

install: build setup.py
	python setup.py install

dist: setup.py MANIFEST.in
	python setup.py sdist --force-manifest

clean:
	python setup.py clean
	rm -rf build
	rm -rf dist
	rm -f csudoku.so
	rm -f *.pyc

.PHONY: test
test: build
	nosetests test/test_*.py

.PHONY: test-cover
test-cover: build
	nosetests --with-coverage --cover-inclusive --cover-erase test/test_*.py
