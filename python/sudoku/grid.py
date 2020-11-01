class Grid:
    def __init__(self, values=None):
        if values is None:
            values = [0 for _ in range(81)]
        self.values = values

    # For testing
    def __eq__(self, other):
        return isinstance(other, Grid) and self.values == other.values

    @classmethod
    def from_string(cls, input):
        """
        Load a grid from a string.

        ``input`` represents non-empty cells with a digit and empty cells
        with "_", ".", or " ". Line breaks are optional.

        """
        # Normalize input to a string of 81 characters.
        # We attempt to support two formats:
        # - one line of 81 characters — best for line-oriented processing;
        # - nine lines of nine characters - closer to the usual format.
        # We compensate for missing trailing spaces and trailing newlines.
        rows = input.splitlines()
        if len(rows) == 1 and len(rows[0]) <= 81:
            values = rows[0].ljust(81)
        elif len(rows) == 9 and all(len(row) <= 9 for row in rows):
            values = "".join(row.ljust(9) for row in rows)
        else:
            raise ValueError(f"input isn't a 9x9 grid: {input!r}")

        for cell in values:
            if cell not in " ._123456789":
                raise ValueError(f"cell contains invalid value: {cell!r}")

        values = values.replace(" ", "0").replace(".", "0").replace("_", "0")
        return cls([int(cell) for cell in values])

    def to_string(self, format):
        """
        Serialize a grid to a string.

        Supported ``format`` values are:

        - console: for human-friendly display in a console
        - grid: nine lines of nine characters, accepted by ``from_string``;
        - line: one line of 81 characters, accepted by ``from_string``;
        - html: for human-friendly display in a web browser

        console and grid include a trailing newline; line and html don't.

        """
        if format not in ["console", "grid", "line", "html"]:
            raise ValueError(f"unsupported format: {format}")
        return getattr(self, f"_to_{format}")()

    def _to_console(self):
        values = [" " if value == 0 else str(value) for value in self.values]
        matrix = [values[9 * i : 9 * i + 9] for i in range(9)]
        sep = " --- --- --- --- --- --- --- --- --- \n"
        rows = ["| " + " | ".join(row) + " |\n" for row in matrix]
        return sep + sep.join(rows) + sep

    def _to_grid(self):
        values = ["_" if value == 0 else str(value) for value in self.values]
        matrix = [values[9 * i : 9 * i + 9] for i in range(9)]
        rows = ["".join(row) + "\n" for row in matrix]
        return "".join(rows)

    def _to_line(self):
        values = ["_" if value == 0 else str(value) for value in self.values]
        return "".join(values)

    def _to_html(self):
        values = [" " if value == 0 else str(value) for value in self.values]
        matrix = [values[9 * i : 9 * i + 9] for i in range(9)]
        data = [[f"<td>{cell}</td>" for cell in row] for row in matrix]
        rows = ["<tr>" + "".join(row) + "</tr>" for row in data]
        return "<table>" + "".join(rows) + "</table>"
