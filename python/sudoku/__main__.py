import argparse
import sys


def build_parser():
    """
    Build a parser for command-line arguments.

    """
    parser = argparse.ArgumentParser(
        prog="sudoku",
        description="solve or generate Sudoku grids",
    )
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        required=True,
        metavar="<command>",
    )

    # solve commmand

    solve_parser = subparsers.add_parser(
        "solve",
        description="solve Sudoku grid",
        help="solve Sudoku grid",
    )
    solve_parser.add_argument(
        "-e",
        "--estimate",
        action="store_true",
        help="show difficulty estimate",
    )
    solve_parser.add_argument(
        "-f",
        "--format",
        choices=["console", "grid", "line", "html"],
        default="console",
        help="select output format (default: console)",
    )
    solve_parser.add_argument(
        "-i",
        "--input",
        default="-",
        type=argparse.FileType("r"),
        help="read problem from this file (default: - for stdin)",
        metavar="<file>",
    )
    solve_parser.add_argument(
        "-o",
        "--output",
        default="-",
        type=argparse.FileType("w"),
        help="write solution to this file (default: - for stdout)",
        metavar="<file>",
    )
    solve_parser.add_argument(
        "-m",
        "--multiple",
        action="store_true",
        help="allow multiple solutions",
    )
    solve_parser.add_argument(
        "problem",
        nargs="?",
        help="problem, formatted as a 81-character string",
    )

    # generate commmand

    generate_parser = subparsers.add_parser(
        "generate",
        description="generate Sudoku grid",
        help="generate Sudoku grid",
    )
    generate_parser.add_argument(
        "-e",
        "--estimate",
        action="store_true",
        help="show difficulty estimate",
    )
    generate_parser.add_argument(
        "-f",
        "--format",
        choices=["console", "grid", "line", "html"],
        default="console",
        help="select output format (default: console)",
    )
    generate_parser.add_argument(
        "-o",
        "--output",
        default="-",
        type=argparse.FileType("w"),
        help="write problem to this file (default: stdout)",
        metavar="<file>",
    )

    # display command

    display_parser = subparsers.add_parser(
        "display",
        description="display Sudoku grid",
        help="display Sudoku grid",
    )
    display_parser.add_argument(
        "-f",
        "--format",
        choices=["console", "grid", "line", "html"],
        default="console",
        help="select output format (default: console)",
    )
    display_parser.add_argument(
        "-i",
        "--input",
        default="-",
        type=argparse.FileType("r"),
        help="read problem from this file (default: stdin)",
        metavar="<file>",
    )
    display_parser.add_argument(
        "-o",
        "--output",
        default="-",
        type=argparse.FileType("w"),
        help="write problem to this file (default: stdout)",
        metavar="<file>",
    )
    display_parser.add_argument(
        "problem",
        nargs="?",
        help="problem, formatted as a 81-character string",
    )

    # serve command

    serve_parser = subparsers.add_parser(
        "serve",
        description="start web server",
        help="run web server",
    )
    serve_parser.add_argument(
        "--host",
        default="",
        help="hostname or IP address on which to listen",
    )
    serve_parser.add_argument(
        "-p",
        "--port",
        default=29557,
        type=int,
        help="TCP port on which to listen",
    )
    return parser


def read_grid(input, problem):
    """
    Read the problem provided in argument or in input file.

    """
    from .grid import Grid

    if problem is None:
        problem = input.read()
    try:
        return Grid.from_string(problem)
    except ValueError as exc:
        sys.stderr.write(f"cannot read problem: {exc}\n")
        sys.exit(1)


def write_grid(grid, format, output):
    """
    Write the problem to output file.

    """
    problem = grid.to_string(format)
    if problem[-1] != "\n":
        problem += "\n"
    output.write(problem)


def solve_cmd(estimate, format, input, output, multiple, problem):
    """
    Implement the solve command.

    """
    from .solver import solve

    grid = read_grid(input, problem)
    solutions, difficulty = solve(grid)
    if len(solutions) == 1:
        grid = solutions[0]
        write_grid(grid, format, output)
    elif len(solutions) == 0:
        sys.stderr.write("no solution found\n")
        sys.exit(1)
    else:  # len(solutions) > 1
        if multiple:
            for grid in solutions:
                write_grid(grid, format, output)
        else:
            sys.stderr.write(f"multiple solutions found ({len(solutions)})\n")
            sys.exit(1)
    if estimate:
        sys.stderr.write(f"Difficulty: {difficulty:.2f}\n")


def generate_cmd(estimate, format, output):
    """
    Implement the generate command.

    """
    from .generator import generate

    grid, difficulty = generate()
    write_grid(grid, format, output)
    if estimate:
        sys.stderr.write(f"Difficulty: {difficulty:.2f}\n")


def display_cmd(format, input, output, problem):
    """
    Implement the display command.

    """
    grid = read_grid(input, problem)
    write_grid(grid, format, output)


def serve_cmd(host, port):  # pragma: no cover
    """
    Implement the serve command.

    """
    from wsgiref.simple_server import make_server

    from .server import application

    with make_server(host, port, application) as server:
        print("Serving on http://{}:{}/".format(*server.server_address))
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print()


def main(args=None):
    """
    Implement the sudoku program.

    """
    parser = build_parser()
    namespace = parser.parse_args(args)
    kwargs = vars(namespace)
    # Make problem and --stdin arguments mutually exclusive.
    if kwargs.get("problem") is not None and kwargs["input"] != sys.stdin:
        parser.error("argument --input: not allowed with argument problem")
    command = kwargs.pop("command")
    globals()[f"{command}_cmd"](**kwargs)


if __name__ == "__main__":  # pragma: no cover
    main()
