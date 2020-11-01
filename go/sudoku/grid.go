package sudoku

import (
	"fmt"
	"strings"
)

type Grid [81]uint8

// Load a grid from a string.
//
// values represents non-empty cells with a digit and empty cells
// with "_", ".", or " ". Line breaks are optional.
func NewGridFromString(input string) (Grid, error) {
	var grid Grid
	var values string

	// Normalize input to a string of 81 characters.
	// We attempt to support two formats:
	// - one line of 81 characters — best for line-oriented processing;
	// - nine lines of nine characters - closer to the usual format.
	// We compensate for missing trailing spaces.
	normalized := strings.ReplaceAll(input, "\r\n", "\n")
	normalized = strings.ReplaceAll(normalized, "\r", "\n")
	normalized = strings.TrimSuffix(normalized, "\n")

	lines := strings.Split(normalized, "\n")
	if len(lines) == 1 {
		line := lines[0]
		if len(line) > 81 {
			return grid, fmt.Errorf("input isn't a 9x9 grid: %q", input)
		} else if len(line) < 81 {
			lines[0] = line + strings.Repeat("_", 81-len(line))
		}
		values = lines[0]
	} else if len(lines) == 9 {
		for i, line := range lines {
			if len(line) > 9 {
				return grid, fmt.Errorf("input isn't a 9x9 grid: %q", input)
			} else if len(line) < 9 {
				lines[i] = line + strings.Repeat("_", 9-len(line))
			}
		}
		values = strings.Join(lines, "")
	} else {
		return grid, fmt.Errorf("input isn't a 9x9 grid: %q", input)
	}

	for i, cell := range values {
		switch cell {
		case '_', '.', ' ':
		case '1', '2', '3', '4', '5', '6', '7', '8', '9':
			grid[i] = uint8(cell) - '0'
		default:
			return grid, fmt.Errorf("cell contains invalid value: %q", cell)
		}
	}
	return grid, nil
}

// Serialize a grid to string.
//
// Supported ``format`` values are:
//
// - console: for human-friendly display in a console
// - grid: nine lines of nine characters, accepted by ``NewGridFromString``;
// - line: one line of 81 characters, accepted by ``NewGridFromString``;
// - html: for human-friendly display in a web browser
//
// console and grid include a trailing newline; line and html don't.
func (grid *Grid) ToString(format string) (string, error) {
	switch format {
	case "console":
		return grid.toConsole(), nil
	case "grid":
		return grid.toGrid(), nil
	case "line":
		return grid.toLine(), nil
	case "html":
		return grid.toHTML(), nil
	default:
		return "", fmt.Errorf("unsupported format: %s", format)
	}
}

func (grid *Grid) toConsole() string {
	var output strings.Builder
	for i := 0; i < 9; i++ {
		output.WriteString(" --- --- --- --- --- --- --- --- --- \n")
		for j := 0; j < 9; j++ {
			cell := grid[9*i+j]
			if cell == 0 {
				output.WriteString("|   ")
			} else {
				output.WriteString("| " + string('0'+cell) + " ")
			}
		}
		output.WriteString("|\n")
	}
	output.WriteString(" --- --- --- --- --- --- --- --- --- \n")
	return output.String()
}

func (grid *Grid) toGrid() string {
	var output strings.Builder
	for i := 0; i < 9; i++ {
		for j := 0; j < 9; j++ {
			cell := grid[9*i+j]
			if cell == 0 {
				output.WriteString("_")
			} else {
				output.WriteString(string('0' + cell))
			}
		}
		output.WriteString("\n")
	}
	return output.String()
}

func (grid *Grid) toLine() string {
	var output strings.Builder
	for _, cell := range grid {
		if cell == 0 {
			output.WriteString("_")
		} else {
			output.WriteString(string('0' + cell))
		}
	}
	return output.String()
}

func (grid *Grid) toHTML() string {
	var output strings.Builder
	output.WriteString("<table>")
	for i := 0; i < 9; i++ {
		output.WriteString("<tr>")
		for j := 0; j < 9; j++ {
			cell := grid[9*i+j]
			if cell == 0 {
				output.WriteString("<td> </td>")
			} else {
				output.WriteString("<td>" + string('0'+cell) + "</td>")
			}
		}
		output.WriteString("</tr>")
	}
	output.WriteString("</table>")
	return output.String()
}
