.PHONY: style test coverage benchmark clean

style:
	go fmt ./sudoku ./sudoku/cmd/sudoku

test:
	go test ./sudoku

coverage:
	go test -coverprofile=cover.out ./sudoku
	go tool cover -html=cover.out

benchmark:
	go test -bench=. ./sudoku

clean:
	rm cover.out
