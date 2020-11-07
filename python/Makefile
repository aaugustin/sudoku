.PHONY: style test coverage benchmark clean

style:
	python -m black .

test:
	python -m unittest

coverage:
	python -m coverage run -m unittest
	python -m coverage html
	python -m webbrowser file://${CURDIR}/htmlcov/index.html

benchmark:
	python -m benchmark

clean:
	python -m coverage erase
	rm -r htmlcov
