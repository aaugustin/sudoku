import io
import pathlib
import random
import sys
import tempfile
import unittest

from sudoku.__main__ import main

try:
    from _sudoku import generate, solve  # noqa
except ImportError:
    has_c_extension = False
else:  # pragma: no cover
    has_c_extension = True
    del generate, solve


# Inputs
problem = (
    "_9_________3__6__2___72_____________5_49___1_6__8__37__1_3__4_9_7__6_1_____5___8_"
)
problem2 = (
    "_9_________3__6__2____2_____________5_49___1_6__8__37__1_3__4_9_7__6_1_____5___8_"
)
problem3 = (
    "_9_________3__6__2___62_____________5_49___1_6__8__37__1_3__4_9_7__6_1_____5___8_"
)

# Outputs
problem_console = "^ --- --- --- --- --- --- --- --- --- \n|   | 9 |   |   |   |   |   |   |   |\n --- --- --- --- --- --- --- --- --- \n|   |   | 3 |   |   | 6 |   |   | 2 |\n --- --- --- --- --- --- --- --- --- \n|   |   |   | 7 | 2 |   |   |   |   |\n --- --- --- --- --- --- --- --- --- \n|   |   |   |   |   |   |   |   |   |\n --- --- --- --- --- --- --- --- --- \n| 5 |   | 4 | 9 |   |   |   | 1 |   |\n --- --- --- --- --- --- --- --- --- \n| 6 |   |   | 8 |   |   | 3 | 7 |   |\n --- --- --- --- --- --- --- --- --- \n|   | 1 |   | 3 |   |   | 4 |   | 9 |\n --- --- --- --- --- --- --- --- --- \n|   | 7 |   |   | 6 |   | 1 |   |   |\n --- --- --- --- --- --- --- --- --- \n|   |   |   | 5 |   |   |   | 8 |   |\n --- --- --- --- --- --- --- --- --- \n$"
problem_grid = "^_9_______\n__3__6__2\n___72____\n_________\n5_49___1_\n6__8__37_\n_1_3__4_9\n_7__6_1__\n___5___8_\n$"
problem_line = "^_9_________3__6__2___72_____________5_49___1_6__8__37__1_3__4_9_7__6_1_____5___8_\n$"
solution_console = "^ --- --- --- --- --- --- --- --- --- \n| 7 | 9 | 2 | 4 | 5 | 8 | 6 | 3 | 1 |\n --- --- --- --- --- --- --- --- --- \n| 8 | 5 | 3 | 1 | 9 | 6 | 7 | 4 | 2 |\n --- --- --- --- --- --- --- --- --- \n| 4 | 6 | 1 | 7 | 2 | 3 | 5 | 9 | 8 |\n --- --- --- --- --- --- --- --- --- \n| 1 | 8 | 7 | 6 | 3 | 5 | 9 | 2 | 4 |\n --- --- --- --- --- --- --- --- --- \n| 5 | 3 | 4 | 9 | 7 | 2 | 8 | 1 | 6 |\n --- --- --- --- --- --- --- --- --- \n| 6 | 2 | 9 | 8 | 4 | 1 | 3 | 7 | 5 |\n --- --- --- --- --- --- --- --- --- \n| 2 | 1 | 5 | 3 | 8 | 7 | 4 | 6 | 9 |\n --- --- --- --- --- --- --- --- --- \n| 9 | 7 | 8 | 2 | 6 | 4 | 1 | 5 | 3 |\n --- --- --- --- --- --- --- --- --- \n| 3 | 4 | 6 | 5 | 1 | 9 | 2 | 8 | 7 |\n --- --- --- --- --- --- --- --- --- \n$"
solution_grid = "^792458631\n853196742\n461723598\n187635924\n534972816\n629841375\n215387469\n978264153\n346519287\n$"
solution_line = "^792458631853196742461723598187635924534972816629841375215387469978264153346519287\n$"
difficulty = "^Difficulty: 2.22\n$"
solution2_line = "^792458631853196742461723598187635924534972816629841375215387469978264153346519287\n492758631853196742167423598781635924534972816629841375215387469978264153346519287\n492758631853196742761423598187635924534972816629841375215387469978264153346519287\n492158736153796842867423591781635924534972618629841375215387469978264153346519287\n$"

# Testing style requires a deterministic random generator, but the C extension
# relies on a system generator that cannot be seeded easily.
@unittest.skipIf(has_c_extension, "incompatible with the C extension")
class TestMain(unittest.TestCase):
    def assertCommand(self, args, in_, code, out, err):
        # Convert pathlib.Path instances to strings
        args = [str(arg) for arg in args]

        # Make test deterministic
        random.seed(18383222420692992)  # there's 9! times this number of grids

        oldin, oldout, olderr = sys.stdin, sys.stdout, sys.stderr
        sys.stdin, sys.stdout, sys.stderr = (
            io.StringIO(in_),
            io.StringIO(),
            io.StringIO(),
        )

        try:
            try:
                main(args)
            except SystemExit as exc:
                self.assertEqual(exc.code, code)
            else:
                self.assertEqual(0, code)
            if out != "" and out[0] == "^" and out[-1] == "$":
                self.assertEqual(sys.stdout.getvalue(), out[1:-1])
            else:
                self.assertIn(out, sys.stdout.getvalue())
            if err != "" and err[0] == "^" and err[-1] == "$":
                self.assertEqual(sys.stderr.getvalue(), err[1:-1])
            else:
                self.assertIn(err, sys.stderr.getvalue())
        finally:
            sys.stdin, sys.stdout, sys.stderr = oldin, oldout, olderr

    def test_solve(self):
        tmp_dir_obj = tempfile.TemporaryDirectory(prefix="sudoku-main-test-")
        self.addCleanup(tmp_dir_obj.cleanup)
        tmp_dir = pathlib.Path(tmp_dir_obj.name)

        input_file = tmp_dir / "input.sdk"
        input_file.write_text(problem)

        output_file = tmp_dir / "output.sdk"

        # fmt: off
        tests = [
            # Successes
            (["solve", problem], "", 0, solution_console, ""),
            (["solve"], problem, 0, solution_console, ""),
            (["solve", "-e", problem], "", 0, solution_console, difficulty),
            (["solve", "-f", "grid", problem], "", 0, solution_grid, ""),
            (["solve", "--format", "line", "--estimate", problem], "", 0, solution_line, difficulty),
            (["solve", "--format", "line", "--multiple", problem2], "", 0, solution2_line, ""),
            (["solve", "-i", input_file, "-o", output_file], "", 0, "", ""),  # see gross hack below

            # Runtime errors
            (["solve", problem2], "", 1, "", "^multiple solutions found\n$"),
            (["solve", problem3], "", 1, "", "^no solution found\n$"),
            (["solve", "-m", problem3], "", 1, "", "^no solution found\n$"),
            (["solve", "ABC"], "", 1, "", "cannot read problem: cell contains invalid value"),

            # Usage errors
            (["solve", "-i", tmp_dir / "does-not-exist.sdk"], "", 2, "", "argument -i/--input: can't open"),
            (["solve", "-o", tmp_dir / "does-not-exist/output.sdk", problem], "", 2, "", "argument -o/--output: can't open"),
            (["solve", "-o", tmp_dir / "does-not-exist/output.sdk", "-m", problem2], "", 2, "", "argument -o/--output: can't open"),
            (["solve", "-f", "3d", problem], "", 2, "", "argument -f/--format: invalid choice: '3d'"),
            (["solve", "-z"], "", 2, "", "unrecognized arguments: -z"),
            (["solve", problem, problem], "", 2, "", "unrecognized arguments"),
            (["solve", "-i", input_file, problem], "", 2, "", "argument --input: not allowed with argument problem"),
        ]
        # fmt: on
        for args, in_, code, out, err in tests:
            with self.subTest(args=args, stdin=in_):
                self.assertCommand(args, in_, code, out, err)
                if "-o" in args and code == 0:  # gross hack
                    self.assertEqual(output_file.read_text(), solution_console[1:-1])
                    output_file.unlink()

    def test_generate(self):
        tmp_dir_obj = tempfile.TemporaryDirectory(prefix="sudoku-main-test-")
        self.addCleanup(tmp_dir_obj.cleanup)
        tmp_dir = pathlib.Path(tmp_dir_obj.name)

        output_file = tmp_dir / "output.sdk"

        # fmt: off
        tests = [
            # Successes
            (["generate"], "", 0, problem_console, ""),
            (["generate", "-e"], "", 0, problem_console, difficulty),
            (["generate", "-f", "grid"], "", 0, problem_grid, ""),
            (["generate", "--format", "line", "--estimate"], "", 0, problem_line, difficulty),
            (["generate", "-o", output_file], "", 0, "", ""),  # see gross hack below

            # Usage errors
            (["generate", "-f", "3d"], "", 2, "", "argument -f/--format: invalid choice: '3d'"),
            (["generate", "-z"], "", 2, "", "unrecognized arguments: -z"),
            (["generate", problem], "", 2, "", "unrecognized arguments"),
        ]
        # fmt: on
        for args, in_, code, out, err in tests:
            with self.subTest(args=args, stdin=in_):
                self.assertCommand(args, in_, code, out, err)
                if "-o" in args and code == 0:  # gross hack
                    self.assertEqual(output_file.read_text(), problem_console[1:-1])
                    output_file.unlink()

    def test_display(self):
        tmp_dir_obj = tempfile.TemporaryDirectory(prefix="sudoku-main-test-")
        self.addCleanup(tmp_dir_obj.cleanup)
        tmp_dir = pathlib.Path(tmp_dir_obj.name)

        input_file = tmp_dir / "input.sdk"
        input_file.write_text(problem)

        output_file = tmp_dir / "output.sdk"

        # fmt: off
        tests = [
            # Successes
            (["display", problem], "", 0, problem_console, ""),
            (["display"], problem, 0, problem_console, ""),
            (["display", "-f", "grid", problem], "", 0, problem_grid, ""),
            (["display", "-i", input_file, "-o", output_file], "", 0, "", ""),  # see gross hack below

            # Runtime errors
            (["display", "ABC"], "", 1, "", "cannot read problem: cell contains invalid value: 'A'"),

            # Usage errors
            (["display", "-i", tmp_dir / "does-not-exist.sdk"], "", 2, "", "argument -i/--input: can't open"),
            (["display", "-o", tmp_dir / "does-not-exist/output.sdk"], "", 2, "", "argument -o/--output: can't open"),
            (["display", "-f", "3d", problem], "", 2, "", "argument -f/--format: invalid choice: '3d'"),
            (["display", "-z"], "", 2, "", "unrecognized arguments: -z"),
            (["display", problem, problem], "", 2, "", "unrecognized arguments"),
            (["display", "-i", input_file, problem], "", 2, "", "argument --input: not allowed with argument problem"),
        ]
        # fmt: on
        for args, in_, code, out, err in tests:
            with self.subTest(args=args, stdin=in_):
                self.assertCommand(args, in_, code, out, err)
                if "-o" in args and code == 0:  # gross hack
                    self.assertEqual(output_file.read_text(), problem_console[1:-1])
                    output_file.unlink()

    def test_serve(self):
        # fmt: off
        tests = [
            # Usage errors
            (["serve", "-z"], "", 2, "", "unrecognized arguments: -z"),
            (["serve", problem], "", 2, "", "unrecognized arguments"),
        ]
        # fmt: on
        for args, in_, code, out, err in tests:
            with self.subTest(args=args, stdin=in_):
                self.assertCommand(args, in_, code, out, err)

    def test_misc(self):
        # fmt: off
        tests = [
            # Help
            (["-h"], "", 0, "usage: sudoku", ""),
            (["--help"], "", 0, "usage: sudoku", ""),

            # Usage errors
            (["sudoku"], "", 2, "", "usage: sudoku"),
            (["zzz"], "", 2, "", "usage: sudoku"),
        ]
        # fmt: on
        for args, in_, code, out, err in tests:
            with self.subTest(args=args, stdin=in_):
                self.assertCommand(args, in_, code, out, err)
