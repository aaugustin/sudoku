import pathlib
import string

from .generator import generate
from .grid import Grid
from .solver import solve

ASSETS_DIR = pathlib.Path(__file__).parent / "assets"

TEMPLATE = string.Template(
    """<!DOCTYPE html>
<html lang="en">
    <head>
        <meta name="viewport" content="initial-scale=1">
        <title>Sudoku</title>
        <style>
"""
    + (ASSETS_DIR / "style.css").read_text().replace("$", "$$")
    + """
        </style>
    </head>
    <body>
        <header>
            ${stars}
        </header>
        ${display}
        <footer>
            <a href="/">New grid</a>
            -
            <a href="/problem/${link}">Problem</a>
            -
            <a href="/solution/${link}">Solution</a>
        </footer>
        <script>
"""
    + (ASSETS_DIR / "script.js").read_text().replace("$", "$$")
    + """
        </script>
    </body>
</html>
"""
)


def render_grid(start_response, display, link, difficulty):
    stars = min(int(difficulty), 5)
    body = TEMPLATE.substitute(
        stars=stars * "★" + (5 - stars) * "☆",
        display=display._to_html().replace(
            "<td></td>",
            "<td contenteditable><br></td>",
        ),
        link=link._to_line(),
    ).encode()
    start_response(
        "200 OK",
        [
            ("Content-Type", "text/html; charset=utf-8"),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


def render_error(start_response, status, message):
    body = message.encode()
    start_response(
        status,
        [
            ("Content-Type", "text/plain; charset=utf-8"),
            ("X-Content-Type-Options", "nosniff"),
            ("Content-Length", str(len(body))),
        ],
    )
    return [body]


def render_redirect(start_response, location):
    start_response(
        "302 Found",
        [("Location", location)],
    )
    return []


def application(environ, start_response):
    """
    WSGI application for the web server.

    """
    method = environ["REQUEST_METHOD"]
    if method != "GET":
        return render_error(
            start_response,
            "405 Method Not Allowed",
            f"{method} not allowed",
        )

    path = environ["PATH_INFO"]
    if path == "/":
        grid, _ = generate()
        return render_redirect(
            start_response,
            f"/problem/{grid._to_line()}",
        )

    elif path.startswith("/problem/"):
        problem = path[len("/problem/") :]
        try:
            grid = Grid.from_string(problem)
        except ValueError as exc:
            return render_error(
                start_response,
                "400 Bad Request",
                str(exc),
            )
        solutions, difficulty = solve(grid)
        if not solutions:
            return render_error(
                start_response,
                "400 Bad Request",
                "no solution found",
            )
        if len(solutions) > 1:
            return render_error(
                start_response,
                "400 Bad Request",
                "multiple solutions found",
            )
        return render_grid(start_response, grid, grid, difficulty)

    elif path.startswith("/solution/"):
        problem = path[len("/solution/") :]
        try:
            grid = Grid.from_string(problem)
        except ValueError as exc:
            return render_error(
                start_response,
                "400 Bad Request",
                str(exc),
            )
        solutions, difficulty = solve(grid)
        if not solutions:
            return render_error(
                start_response,
                "400 Bad Request",
                "no solution found",
            )
        if len(solutions) > 1:
            return render_error(
                start_response,
                "400 Bad Request",
                "multiple solutions found",
            )
        return render_grid(start_response, solutions[0], grid, difficulty)

    return render_error(
        start_response,
        "404 Not Found",
        f"{path} not found",
    )
