.PHONY: style build test coverage benchmark clean

style:
	python -m black .

build:
	python setup.py build_ext --inplace

test:
	python -m unittest

coverage:
	python -m coverage run -m unittest
	python -m coverage html
	python -m webbrowser file://${CURDIR}/htmlcov/index.html

benchmark:
	python -m benchmark solve
	python -m benchmark generate

clean:
	python -m coverage erase
	rm -rf build htmlcov
	rm -f _sudoku.*
