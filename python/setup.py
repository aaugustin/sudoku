from setuptools import setup

setup(
    name="sudoku",
    version="4.0",
    author="Aymeric Augustin",
    author_email="aymeric.augustin@m4x.org",
    license="Proprietary",
    description="SuDoKu solver and generator",
    long_description=(
        "Library and command-line utility to solve and generate SuDoKu grids"
    ),
    url="https://github.com/aaugustin/sudoku",
    packages=["sudoku"],
    entry_points={"console_scripts": ["sudoku=sudoku.__main__:main"]},
)
