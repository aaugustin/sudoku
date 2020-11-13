import argparse


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


def solve_cmd(estimate, format, input, output, multiple, problem):
    """
    Implement the solve command.

    """
    from .grid import Grid
    from .solver import solve

    if problem is None:
        problem = input.read()
    grid = Grid.from_string(problem)
    for solution in solve(grid):
        output.write(solution.to_string(format))


def generate_cmd(estimate, format, output):
    """
    Implement the generate command.

    """
    from .generator import generate

    grid = generate()
    output.write(grid.to_string(format))


def display_cmd(format, input, output, problem):
    """
    Implement the display command.

    """
    from .grid import Grid

    if problem is None:
        problem = input.read()
    grid = Grid.from_string(problem)
    output.write(grid.to_string(format))


def serve_cmd(host, port):
    """
    Implement the serve command.

    """
    from wsgiref.simple_server import make_server

    from .server import application

    with make_server(host, port, application) as server:
        if host == "":
            host = "localhost"
        print(f"Serving on http://{host}:{port}/")
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
    if kwargs.get("problem") is not None and kwargs["input"].fileno() != 0:
        parser.error("argument --input: not allowed with argument problem")
    command = kwargs.pop("command")
    globals()[f"{command}_cmd"](**kwargs)


if __name__ == "__main__":
    main()
