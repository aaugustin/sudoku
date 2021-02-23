package main

import (
	"bytes"
	"io/ioutil"
	"math/rand"
	"os"
	"strings"
	"testing"
)

// Inputs
var problem string = "__43_87___15______8_______9___8__351___2_5_____3___9__5___9_684____7_______4____2"
var problem2 string = "__43_87___15______8_______9___8__3_1___2_5_____3___9__5___9_684____7_______4____2"
var problem3 string = "__43_87___15______8_______9___8__341___2_5_____3___9__5___9_684____7_______4____2"

// Outputs
var problemConsole string = "^ --- --- --- --- --- --- --- --- --- \n|   |   | 4 | 3 |   | 8 | 7 |   |   |\n --- --- --- --- --- --- --- --- --- \n|   | 1 | 5 |   |   |   |   |   |   |\n --- --- --- --- --- --- --- --- --- \n| 8 |   |   |   |   |   |   |   | 9 |\n --- --- --- --- --- --- --- --- --- \n|   |   |   | 8 |   |   | 3 | 5 | 1 |\n --- --- --- --- --- --- --- --- --- \n|   |   |   | 2 |   | 5 |   |   |   |\n --- --- --- --- --- --- --- --- --- \n|   |   | 3 |   |   |   | 9 |   |   |\n --- --- --- --- --- --- --- --- --- \n| 5 |   |   |   | 9 |   | 6 | 8 | 4 |\n --- --- --- --- --- --- --- --- --- \n|   |   |   |   | 7 |   |   |   |   |\n --- --- --- --- --- --- --- --- --- \n|   |   |   | 4 |   |   |   |   | 2 |\n --- --- --- --- --- --- --- --- --- \n$"
var problemGrid string = "^__43_87__\n_15______\n8_______9\n___8__351\n___2_5___\n__3___9__\n5___9_684\n____7____\n___4____2\n$"
var problemLine string = "^__43_87___15______8_______9___8__351___2_5_____3___9__5___9_684____7_______4____2\n$"
var solutionConsole string = "^ --- --- --- --- --- --- --- --- --- \n| 9 | 2 | 4 | 3 | 6 | 8 | 7 | 1 | 5 |\n --- --- --- --- --- --- --- --- --- \n| 7 | 1 | 5 | 9 | 2 | 4 | 8 | 3 | 6 |\n --- --- --- --- --- --- --- --- --- \n| 8 | 3 | 6 | 7 | 5 | 1 | 2 | 4 | 9 |\n --- --- --- --- --- --- --- --- --- \n| 2 | 6 | 7 | 8 | 4 | 9 | 3 | 5 | 1 |\n --- --- --- --- --- --- --- --- --- \n| 1 | 8 | 9 | 2 | 3 | 5 | 4 | 6 | 7 |\n --- --- --- --- --- --- --- --- --- \n| 4 | 5 | 3 | 6 | 1 | 7 | 9 | 2 | 8 |\n --- --- --- --- --- --- --- --- --- \n| 5 | 7 | 2 | 1 | 9 | 3 | 6 | 8 | 4 |\n --- --- --- --- --- --- --- --- --- \n| 6 | 4 | 8 | 5 | 7 | 2 | 1 | 9 | 3 |\n --- --- --- --- --- --- --- --- --- \n| 3 | 9 | 1 | 4 | 8 | 6 | 5 | 7 | 2 |\n --- --- --- --- --- --- --- --- --- \n$"
var solutionGrid string = "^924368715\n715924836\n836751249\n267849351\n189235467\n453617928\n572193684\n648572193\n391486572\n$"
var solutionLine string = "^924368715715924836836751249267849351189235467453617928572193684648572193391486572\n$"
var difficulty string = "^Difficulty: 2.58\n$"
var solution2Line string = "^924368715715924836836751249267849351189235467453617928572193684648572193391486572\n924368715715924836836751249657849321189235467243617958572193684468572193391486572\n924318756615927438837654219756849321149235867283761945572193684468572193391486572\n924358716715964238836721459257849361169235847483617925572193684648572193391486572\n924358716715964238836721459657849321149235867283617945572193684468572193391486572\n924358716615927438837614259756849321149235867283761945572193684468572193391486572\n$"

func testDispatch(t *testing.T, args []string, in string, code int, out string, err string) {
	// Make test deterministic
	rand.Seed(18383222420692992) // there's 9! times this number of grids

	oldin, oldout, olderr := stdin, stdout, stderr
	tstin, tstout, tsterr := bytes.NewBufferString(in), new(bytes.Buffer), new(bytes.Buffer)
	stdin, stdout, stderr = tstin, tstout, tsterr
	defer func() { stdin, stdout, stderr = oldin, oldout, olderr }()

	// Reset variables storing flags to their default values between tests
	defer func() {
		estimate = false
		format = "console"
		input = "-"
		output = "-"
		multiple = false
		host = "localhost"
		port = "29557"
	}()

	if exit := dispatch(args); exit != code {
		t.Errorf("%v: exit code = %d, want %d", strings.Join(args, " "), exit, code)
	}

	if out == "" {
		if tstout.String() != "" {
			t.Errorf("%v: got %#v on stdout, want nothing", strings.Join(args, " "), tstout.String())
		}
	} else if out[0] == '^' && out[len(out)-1] == '$' {
		if tstout.String() != out[1:len(out)-1] {
			t.Errorf("%v: got %#v on stdout, want exactly %#v", strings.Join(args, " "), tstout.String(), out[1:len(out)-1])
		}
	} else {
		if !strings.Contains(tstout.String(), out) {
			t.Errorf("%v: got %#v on stdout, want %#v", strings.Join(args, " "), tstout.String(), out)
		}
	}

	if err == "" {
		if tsterr.String() != "" {
			t.Errorf("%v: got %#v on stderr, want nothing", strings.Join(args, " "), tsterr.String())
		}
	} else if err[0] == '^' && err[len(err)-1] == '$' {
		if tsterr.String() != err[1:len(err)-1] {
			t.Errorf("%v: got %#v on stderr, want exactly %#v", strings.Join(args, " "), tsterr.String(), err[1:len(err)-1])
		}
	} else {
		if !strings.Contains(tsterr.String(), err) {
			t.Errorf("%v: got %#v on stderr, want %#v", strings.Join(args, " "), tsterr.String(), err)
		}
	}
}

func checkFileContents(t *testing.T, args []string, filename string, want string) {
	content, err := ioutil.ReadFile(filename)
	if err != nil {
		t.Errorf("%v: failed to read file %s", strings.Join(args, " "), filename)
	}
	os.Remove(filename) // no need to handle errors
	got := string(content)
	if want[0] == '^' && want[len(want)-1] == '$' {
		if got != want[1:len(want)-1] {
			t.Errorf("%v: got %#v in %s, want exactly %#v", strings.Join(args, " "), got, filename, want[1:len(want)-1])
		}
	} else {
		if !strings.Contains(got, want) {
			t.Errorf("%v: got %#v in %s, want %#v", strings.Join(args, " "), got, filename, want)
		}
	}
}

func TestSolve(t *testing.T) {
	tmpDir, err := ioutil.TempDir("", "sudoku-main-test-*")
	if err != nil {
		panic("cannot create temporary directory")
	}
	defer os.RemoveAll(tmpDir)

	inputFile := tmpDir + "/input.sdk"
	if err = ioutil.WriteFile(inputFile, []byte(problem), 0644); err != nil {
		panic("cannot create temporary file")
	}
	outputFile := tmpDir + "/output.sdk"

	// Successes
	testDispatch(t, []string{"sudoku", "solve", problem}, "", 0, solutionConsole, "")
	testDispatch(t, []string{"sudoku", "solve"}, problem, 0, solutionConsole, "")
	testDispatch(t, []string{"sudoku", "solve", "-e", problem}, "", 0, solutionConsole, difficulty)
	testDispatch(t, []string{"sudoku", "solve", "-f", "grid", problem}, "", 0, solutionGrid, "")
	testDispatch(t, []string{"sudoku", "solve", "--format", "line", "--estimate", problem}, "", 0, solutionLine, difficulty)
	testDispatch(t, []string{"sudoku", "solve", "--format", "line", "--multiple", problem2}, "", 0, solution2Line, "")

	testDispatch(t, []string{"sudoku", "solve", "-i", inputFile, "-o", outputFile}, "", 0, "", "")
	checkFileContents(t, []string{"sudoku", "solve", "-i", inputFile, "-o", outputFile}, outputFile, solutionConsole)

	// Runtime errors
	testDispatch(t, []string{"sudoku", "solve", problem2}, "", 1, "", "^multiple solutions found\n$")
	testDispatch(t, []string{"sudoku", "solve", problem3}, "", 1, "", "^no solution found\n$")
	testDispatch(t, []string{"sudoku", "solve", "-m", problem3}, "", 1, "", "^no solution found\n$")
	testDispatch(t, []string{"sudoku", "solve", "ABC"}, "", 1, "", "cannot read problem: cell contains invalid value")
	testDispatch(t, []string{"sudoku", "solve", "-i", tmpDir + "/does-not-exist.sdk"}, "", 1, "", "cannot read problem from file")
	testDispatch(t, []string{"sudoku", "solve", "-o", tmpDir + "/does-not-exist/output.sdk", problem}, "", 1, "", "cannot write problem to file")
	testDispatch(t, []string{"sudoku", "solve", "-o", tmpDir + "/does-not-exist/output.sdk", "-m", problem2}, "", 1, "", "cannot write problem to file")
	testDispatch(t, []string{"sudoku", "solve", "-f", "3d", problem}, "", 1, "", "cannot write problem: unsupported format")

	// Usage errors
	testDispatch(t, []string{"sudoku", "solve", "-z"}, "", 2, "", "flag provided but not defined: -z")
	testDispatch(t, []string{"sudoku", "solve", problem, problem}, "", 2, "", "unexpected arguments")
	testDispatch(t, []string{"sudoku", "solve", "-i", inputFile, problem}, "", 2, "", "flag -input not allowed with argument")

}

func TestGenerate(t *testing.T) {
	tmpDir, err := ioutil.TempDir("", "sudoku-main-test-*")
	if err != nil {
		panic("cannot create temporary directory")
	}
	defer os.RemoveAll(tmpDir)

	outputFile := tmpDir + "/output.sdk"

	// Successes
	testDispatch(t, []string{"sudoku", "generate"}, "", 0, problemConsole, "")
	testDispatch(t, []string{"sudoku", "generate", "-e"}, "", 0, problemConsole, difficulty)
	testDispatch(t, []string{"sudoku", "generate", "-f", "grid"}, "", 0, problemGrid, "")
	testDispatch(t, []string{"sudoku", "generate", "--format", "line", "--estimate"}, "", 0, problemLine, difficulty)

	testDispatch(t, []string{"sudoku", "generate", "-o", outputFile}, "", 0, "", "")
	checkFileContents(t, []string{"sudoku", "generate", "-o", outputFile}, outputFile, problemConsole)

	// Runtime errors
	testDispatch(t, []string{"sudoku", "generate", "-f", "3d"}, "", 1, "", "cannot write problem: unsupported format")

	// Usage errors
	testDispatch(t, []string{"sudoku", "generate", "-z"}, "", 2, "", "flag provided but not defined: -z")
	testDispatch(t, []string{"sudoku", "generate", problem}, "", 2, "", "unexpected arguments")
}

func TestDisplay(t *testing.T) {
	tmpDir, err := ioutil.TempDir("", "sudoku-main-test-*")
	if err != nil {
		panic("cannot create temporary directory")
	}
	defer os.RemoveAll(tmpDir)

	inputFile := tmpDir + "/input.sdk"
	if err = ioutil.WriteFile(inputFile, []byte(problem), 0644); err != nil {
		panic("cannot create temporary file")
	}
	outputFile := tmpDir + "/output.sdk"

	// Successes
	testDispatch(t, []string{"sudoku", "display", problem}, "", 0, problemConsole, "")
	testDispatch(t, []string{"sudoku", "display"}, problem, 0, problemConsole, "")
	testDispatch(t, []string{"sudoku", "display", "-f", "grid", problem}, "", 0, problemGrid, "")

	testDispatch(t, []string{"sudoku", "display", "-i", inputFile, "-o", outputFile}, "", 0, "", "")
	checkFileContents(t, []string{"sudoku", "display", "-i", inputFile, "-o", outputFile}, outputFile, problemConsole)

	// Runtime errors
	testDispatch(t, []string{"sudoku", "display", "ABC"}, "", 1, "", "cannot read problem: cell contains invalid value: 'A'")
	testDispatch(t, []string{"sudoku", "display", "-i", tmpDir + "/does-not-exist.sdk"}, "", 1, "", "cannot read problem from file")
	testDispatch(t, []string{"sudoku", "display", "-o", tmpDir + "/does-not-exist/output.sdk"}, "", 1, "", "cannot write problem to file")
	testDispatch(t, []string{"sudoku", "display", "-f", "3d", problem}, "", 1, "", "cannot write problem: unsupported format")

	// Usage errors
	testDispatch(t, []string{"sudoku", "display", "-z"}, "", 2, "", "flag provided but not defined: -z")
	testDispatch(t, []string{"sudoku", "display", problem, problem}, "", 2, "", "unexpected arguments")
	testDispatch(t, []string{"sudoku", "display", "-i", inputFile, problem}, "", 2, "", "flag -input not allowed with argument")
}

func TestServe(t *testing.T) {
	// Runtime errors
	testDispatch(t, []string{"sudoku", "serve", "-p", "65536"}, "", 1, "", "invalid port")

	// Usage errors
	testDispatch(t, []string{"sudoku", "serve", "-z"}, "", 2, "", "flag provided but not defined: -z")
	testDispatch(t, []string{"sudoku", "serve", problem}, "", 2, "", "unexpected arguments")
}

func TestMisc(t *testing.T) {
	// Help
	testDispatch(t, []string{"sudoku", "-h"}, "", 0, "", "Usage of sudoku:")
	testDispatch(t, []string{"sudoku", "--help"}, "", 0, "", "Usage of sudoku:")

	// Usage errors
	testDispatch(t, []string{"sudoku"}, "", 2, "", "Usage of sudoku:")
	testDispatch(t, []string{"sudoku", "zzz"}, "", 2, "", "Usage of sudoku:")
}
