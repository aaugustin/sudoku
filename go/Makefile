.PHONY: style build test coverage benchmark clean

style:
	cd sudoku && go fmt . ./cmd/sudoku

build:
	cd sudoku && go build ./cmd/sudoku

test:
	cd sudoku && go test . ./cmd/sudoku

coverage:
	cd sudoku && go test -coverprofile=cover.out . ./cmd/sudoku
	cd sudoku && go tool cover -html=cover.out

benchmark:
	cd sudoku && go test -bench=BenchmarkSolve -run=X .
	cd sudoku && go test -bench=BenchmarkGenerate -run=X .

clean:
	cd sudoku && rm -f cover.out sudoku sudoku.test
