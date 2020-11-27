package main

import (
	"errors"
	"flag"
	"fmt"
	"io"
	"io/ioutil"
	"math/rand"
	"net"
	"net/http"
	"os"
	"strings"
	"time"

	"github.com/aaugustin/sudoku/go/sudoku"
)

// All output goes to these variables, which can be replaced for testing.
var stdin io.Reader = os.Stdin
var stdout io.Writer = os.Stdout
var stderr io.Writer = os.Stderr

var solveCmd = flag.NewFlagSet("solve", flag.ContinueOnError)
var generateCmd = flag.NewFlagSet("generate", flag.ContinueOnError)
var displayCmd = flag.NewFlagSet("display", flag.ContinueOnError)
var serveCmd = flag.NewFlagSet("serve", flag.ContinueOnError)

var estimate bool
var format string
var input string
var output string
var multiple bool
var host string
var port string

func init() {
	// Bind appropriate flags to variables for each command.

	solveCmd.BoolVar(&estimate, "e", false, "shorthand for estimate")
	solveCmd.BoolVar(&estimate, "estimate", false, "show difficulty estimate")
	solveCmd.StringVar(&format, "f", "console", "shorthand for `format`")
	solveCmd.StringVar(&format, "format", "console", "select output `format`: console, grid, line, or html")
	solveCmd.StringVar(&input, "i", "-", "shorthand for `input`")
	solveCmd.StringVar(&input, "input", "-", "read problem from this `file`; - for stdin)")
	solveCmd.StringVar(&output, "o", "-", "shorthand for `output`")
	solveCmd.StringVar(&output, "output", "-", "write solution to this `file`; - for stdout")
	solveCmd.BoolVar(&multiple, "m", false, "shorthand for multiple")
	solveCmd.BoolVar(&multiple, "multiple", false, "allow multiple solutions")

	generateCmd.BoolVar(&estimate, "e", false, "shorthand for estimate")
	generateCmd.BoolVar(&estimate, "estimate", false, "show difficulty estimate")
	generateCmd.StringVar(&format, "f", "console", "shorthand for `format`")
	generateCmd.StringVar(&format, "format", "console", "select output `format`: console, grid, line, or html")
	generateCmd.StringVar(&output, "o", "-", "shorthand for `output`")
	generateCmd.StringVar(&output, "output", "-", "write solution to this `file`; - for stdout")

	displayCmd.StringVar(&format, "f", "console", "shorthand for `format`")
	displayCmd.StringVar(&format, "format", "console", "select output `format`: console, grid, line, or html")
	displayCmd.StringVar(&input, "i", "-", "shorthand for `input`")
	displayCmd.StringVar(&input, "input", "-", "read problem from this `file`; - for stdin)")
	displayCmd.StringVar(&output, "o", "-", "shorthand for `output`")
	displayCmd.StringVar(&output, "output", "-", "write solution to this `file`; - for stdout")

	serveCmd.StringVar(&host, "host", "localhost", "hostname or IP address on which to listen")
	serveCmd.StringVar(&port, "p", "29557", "TCP port on which to listen")
	serveCmd.StringVar(&port, "port", "29557", "TCP port on which to listen")
}

func usage() {
	fmt.Fprint(
		flag.CommandLine.Output(),
		"Usage of sudoku:\n"+
			"  solve ...\n    \tsolve Sudoku grid\n"+
			"  generate ...\n    \tgenerate Sudoku grid\n"+
			"  display ...\n    \tdisplay Sudoku grid\n"+
			"  serve ...\n    \trun web server\n")
}

// parseArgument extracts at most once argument from the command line. If an
// argument is provided, parseArgument checks that input wasn't specified, as
// this is mutually exclusive.
func parseArgument(input string, args []string) (string, error) {
	switch len(args) {
	case 0:
		return "", nil
	case 1:
		if input != "-" {
			return "", errors.New("flag -input not allowed with argument")
		}
		return args[0], nil
	default:
		return "", errors.New("unexpected arguments: " + strings.Join(args[1:], ", "))
	}

}

// readGrid reads the problem provided in argument, on stdin, or in a file.
func readGrid(input string, problem string) (sudoku.Grid, error) {
	var grid sudoku.Grid

	if problem != "" {
		// read problem from command-line argument

	} else if input == "-" {
		// read problem from standard input
		data, err := ioutil.ReadAll(stdin)
		if err != nil {
			return grid, fmt.Errorf("cannot read problem from stdin: %s", err)
		}
		problem = string(data)

	} else {
		// read problem from a file
		data, err := ioutil.ReadFile(input)
		if err != nil {
			return grid, fmt.Errorf("cannot read problem from file: %s", err)
		}
		problem = string(data)
	}

	grid, err := sudoku.NewGridFromString(problem)
	if err != nil {
		return grid, fmt.Errorf("cannot read problem: %s", err)
	}

	return grid, nil
}

// writeGrid writes the problem to stdout or to a file.
func writeGrid(grid sudoku.Grid, format string, output string) error {
	problem, err := grid.ToString(format)
	if err != nil {
		return fmt.Errorf("cannot write problem: %s", err)
	}

	// append newline for proper display
	if problem[len(problem)-1] != '\n' {
		problem += "\n"
	}

	if output == "-" {
		// write problem to standard output
		_, err := stdout.Write([]byte(problem))
		if err != nil {
			return fmt.Errorf("cannot write problem to stdout: %s", err)
		}

	} else {
		// write problem to a file
		err := ioutil.WriteFile(output, []byte(problem), 0644)
		if err != nil {
			return fmt.Errorf("cannot write problem to file: %s", err)
		}
	}

	return nil
}

// solve implements the solve command.
func solve(estimate bool, format string, input string, output string, multiple bool, problem string) error {
	grid, err := readGrid(input, problem)
	if err != nil {
		return err
	}
	solutions, difficulty := sudoku.Solve(&grid)
	if len(solutions) == 1 {
		grid = solutions[0]
		err = writeGrid(grid, format, output)
		if err != nil {
			return err
		}
	} else if len(solutions) == 0 {
		return errors.New("no solution found")
	} else { // len(solutions) > 1
		if multiple {
			for _, grid = range solutions {
				err = writeGrid(grid, format, output)
				if err != nil {
					return err
				}
			}
		} else {
			return fmt.Errorf("multiple solutions found (%d)", len(solutions))
		}
	}
	if estimate {
		fmt.Fprintf(stderr, "Difficulty: %.2f\n", difficulty)
	}
	return nil
}

// generate implements the generate command.
func generate(estimate bool, format string, output string) error {
	grid, difficulty := sudoku.Generate()
	err := writeGrid(grid, format, output)
	if err != nil {
		return err
	}
	if estimate {
		fmt.Fprintf(stderr, "Difficulty: %.2f\n", difficulty)
	}
	return nil
}

// display implements the display command.
func display(format string, input string, output string, problem string) error {
	grid, err := readGrid(input, problem)
	if err != nil {
		return err
	}
	err = writeGrid(grid, format, output)
	if err != nil {
		return err
	}
	return nil
}

// serve implements the serve command.
func serve(host string, port string) error {
	address := net.JoinHostPort(host, port)
	listener, err := net.Listen("tcp", address)
	if err != nil {
		return err
	}
	fmt.Printf("Serving on http://%s/\n", listener.Addr().String())
	return http.Serve(listener, sudoku.Handler)
}

// dispatch parses a command line and executes the requested command.
// It returns exit code 0 on success, 1 when executing the command fails,
// and 2 when parsing the command line fails.
// It displays an informative error message to stderr before returning.
func dispatch(args []string) int {
	flag.CommandLine.SetOutput(stderr)
	if len(args) < 2 {
		usage()
		return 2
	}

	var problem string
	var err error

	switch args[1] {

	case "solve":
		solveCmd.SetOutput(stderr)
		err = solveCmd.Parse(args[2:])
		if err != nil {
			// Parse displays an error message
			return 2
		}
		problem, err = parseArgument(input, solveCmd.Args())
		if err != nil {
			fmt.Fprintln(solveCmd.Output(), err)
			solveCmd.PrintDefaults()
			return 2
		}
		err = solve(estimate, format, input, output, multiple, problem)
		if err != nil {
			fmt.Fprintln(solveCmd.Output(), err)
			return 1
		}

	case "generate":
		generateCmd.SetOutput(stderr)
		err = generateCmd.Parse(args[2:])
		if err != nil {
			// Parse displays an error message
			return 2
		}
		if len(generateCmd.Args()) > 0 {
			fmt.Fprintln(generateCmd.Output(), "unexpected arguments: "+strings.Join(generateCmd.Args(), ", "))
			return 2
		}
		err = generate(estimate, format, output)
		if err != nil {
			fmt.Fprintln(generateCmd.Output(), err)
			return 1
		}

	case "display":
		displayCmd.SetOutput(stderr)
		err = displayCmd.Parse(args[2:])
		if err != nil {
			// Parse displays an error message
			return 2
		}
		problem, err = parseArgument(input, displayCmd.Args())
		if err != nil {
			fmt.Fprintln(displayCmd.Output(), err)
			displayCmd.PrintDefaults()
			return 2
		}
		err = display(format, input, output, problem)
		if err != nil {
			fmt.Fprintln(displayCmd.Output(), err)
			return 1
		}

	case "serve":
		serveCmd.SetOutput(stderr)
		err = serveCmd.Parse(args[2:])
		if err != nil {
			// Parse displays an error message
			return 2
		}
		if len(serveCmd.Args()) > 0 {
			fmt.Fprintln(serveCmd.Output(), "unexpected arguments: "+strings.Join(serveCmd.Args(), ", "))
			return 2
		}
		err = serve(host, port)
		if err != nil {
			fmt.Fprintln(serveCmd.Output(), err)
			return 1
		}

	case "-h", "-help", "--help":
		usage()
		return 0

	default:
		fmt.Fprintln(flag.CommandLine.Output(), "command not supported:", args[1])
		usage()
		return 2

	}

	return 0
}

func main() {
	rand.Seed(time.Now().UTC().UnixNano())
	os.Exit(dispatch(os.Args))
}
