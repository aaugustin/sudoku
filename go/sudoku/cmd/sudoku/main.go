package main

import (
	"errors"
	"flag"
	"fmt"
	"os"
	"strings"
)

var solveCmd = flag.NewFlagSet("solve", flag.ContinueOnError)
var generateCmd = flag.NewFlagSet("generate", flag.ContinueOnError)
var displayCmd = flag.NewFlagSet("display", flag.ContinueOnError)

var estimate bool
var format string
var input string
var output string
var multiple bool

func init() {
	// Bind appropriate flags to variables for each command.

	solveCmd.BoolVar(&estimate, "e", false, "shorthand for estimate")
	solveCmd.BoolVar(&estimate, "estimate", false, "show difficulty estimate")
	solveCmd.StringVar(&format, "f", "console", "shorthand for `format`")
	solveCmd.StringVar(&format, "format", "console", "select output `format`: console, grid, line, or html")
	solveCmd.StringVar(&input, "i", "", "shorthand for `input`")
	solveCmd.StringVar(&input, "input", "-", "read problem from this `file`; - for stdin)")
	solveCmd.StringVar(&output, "o", "", "shorthand for `output`")
	solveCmd.StringVar(&output, "output", "-", "write solution to this `file`; - for stdout")
	solveCmd.BoolVar(&multiple, "m", false, "shorthand for multiple")
	solveCmd.BoolVar(&multiple, "multiple", false, "allow multiple solutions")

	generateCmd.BoolVar(&estimate, "e", false, "shorthand for estimate")
	generateCmd.BoolVar(&estimate, "estimate", false, "show difficulty estimate")
	generateCmd.StringVar(&format, "f", "console", "shorthand for `format`")
	generateCmd.StringVar(&format, "format", "console", "select output `format`: console, grid, line, or html")
	generateCmd.StringVar(&output, "o", "", "shorthand for `output`")
	generateCmd.StringVar(&output, "output", "-", "write solution to this `file`; - for stdout")

	displayCmd.StringVar(&format, "f", "console", "shorthand for `format`")
	displayCmd.StringVar(&format, "format", "console", "select output `format`: console, grid, line, or html")
	displayCmd.StringVar(&input, "i", "", "shorthand for `input`")
	displayCmd.StringVar(&input, "input", "-", "read problem from this `file`; - for stdin)")
	displayCmd.StringVar(&output, "o", "", "shorthand for `output`")
	displayCmd.StringVar(&output, "output", "-", "write solution to this `file`; - for stdout")
}

func usage() {
	fmt.Fprint(
		flag.CommandLine.Output(),
		"Usage of sudoku:\n"+
			"  solve ...\n    \tsolve Sudoku grid\n"+
			"  generate ...\n    \tgenerate Sudoku grid\n"+
			"  display ...\n    \tdisplay Sudoku grid\n")
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
		return "", errors.New("multiple arguments provided: " + strings.Join(args, ", "))
	}

}

func solve(estimate bool, format string, input string, output string, multiple bool, problem string) error {
	// TODO
	return nil
}

func generate(estimate bool, format string, output string) error {
	// TODO
	return nil
}

func display(format string, input string, output string, problem string) error {
	// TODO
	return nil
}

// dispatch parses a command line and executes the requested command.
// It returns exit code 0 on success, 1 when executing the command fails,
// and 2 when parsing the command line fails.
// It displays an informative error message to stderr before returning.
func dispatch(args []string) int {
	if len(os.Args) < 2 {
		usage()
		return 2
	}

	var problem string
	var err error

	switch os.Args[1] {

	case "solve":
		err = solveCmd.Parse(os.Args[2:])
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
		err = generateCmd.Parse(os.Args[2:])
		if err != nil {
			// Parse displays an error message
			return 2
		}
		err = generate(estimate, format, output)
		if err != nil {
			fmt.Fprintln(generateCmd.Output(), err)
			return 1
		}

	case "display":
		err = displayCmd.Parse(os.Args[2:])
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

	case "-h", "-help", "--help":
		usage()
		return 0

	default:
		fmt.Fprintln(displayCmd.Output(), "command not supported:", args[1])
		usage()
		return 2

	}

	return 0
}

func main() {
	os.Exit(dispatch(os.Args))
}