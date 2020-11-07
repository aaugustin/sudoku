package sudoku

import (
	"bufio"
	"os"
	"testing"
)

func TestSolve(t *testing.T) {
	var tests = []struct {
		input Grid
		want  []Grid
	}{
		// one solution, solved without search
		{
			Grid{5, 3, 0, 0, 7, 0, 0, 0, 0, 6, 0, 0, 1, 9, 5, 0, 0, 0, 0, 9, 8, 0, 0, 0, 0, 6, 0, 8, 0, 0, 0, 6, 0, 0, 0, 3, 4, 0, 0, 8, 0, 3, 0, 0, 1, 7, 0, 0, 0, 2, 0, 0, 0, 6, 0, 6, 0, 0, 0, 0, 2, 8, 0, 0, 0, 0, 4, 1, 9, 0, 0, 5, 0, 0, 0, 0, 8, 0, 0, 7, 9},
			[]Grid{
				Grid{5, 3, 4, 6, 7, 8, 9, 1, 2, 6, 7, 2, 1, 9, 5, 3, 4, 8, 1, 9, 8, 3, 4, 2, 5, 6, 7, 8, 5, 9, 7, 6, 1, 4, 2, 3, 4, 2, 6, 8, 5, 3, 7, 9, 1, 7, 1, 3, 9, 2, 4, 8, 5, 6, 9, 6, 1, 5, 3, 7, 2, 8, 4, 2, 8, 7, 4, 1, 9, 6, 3, 5, 3, 4, 5, 2, 8, 6, 1, 7, 9},
			},
		},
		// one solution, solved with search
		{
			Grid{8, 5, 0, 0, 0, 2, 4, 0, 0, 7, 2, 0, 0, 0, 0, 0, 0, 9, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 7, 0, 0, 2, 3, 0, 5, 0, 0, 0, 9, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 8, 0, 0, 7, 0, 0, 1, 7, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 6, 0, 4, 0},
			[]Grid{
				Grid{8, 5, 9, 6, 1, 2, 4, 3, 7, 7, 2, 3, 8, 5, 4, 1, 6, 9, 1, 6, 4, 3, 7, 9, 5, 2, 8, 9, 8, 6, 1, 4, 7, 3, 5, 2, 3, 7, 5, 2, 6, 8, 9, 1, 4, 2, 4, 1, 5, 9, 3, 7, 8, 6, 4, 3, 2, 9, 8, 1, 6, 7, 5, 6, 1, 7, 4, 2, 5, 8, 9, 3, 5, 9, 8, 7, 3, 6, 2, 4, 1},
			},
		},
		// no solutions
		{
			Grid{5, 3, 1, 0, 7, 0, 0, 0, 0, 6, 0, 0, 1, 9, 5, 0, 0, 0, 0, 9, 8, 0, 0, 0, 0, 6, 0, 8, 0, 0, 0, 6, 0, 0, 0, 3, 4, 0, 0, 8, 0, 3, 0, 0, 1, 7, 0, 0, 0, 2, 0, 0, 0, 6, 0, 6, 0, 0, 0, 0, 2, 8, 0, 0, 0, 0, 4, 1, 9, 0, 0, 5, 0, 0, 0, 0, 8, 0, 0, 7, 9},
			[]Grid{},
		},
		// multiple solutions
		{
			Grid{0, 0, 0, 0, 7, 0, 0, 0, 0, 6, 0, 0, 1, 9, 5, 0, 0, 0, 0, 9, 8, 0, 0, 0, 0, 6, 0, 8, 0, 0, 0, 6, 0, 0, 0, 3, 4, 0, 0, 8, 0, 3, 0, 0, 1, 7, 0, 0, 0, 2, 0, 0, 0, 6, 0, 6, 0, 0, 0, 0, 2, 8, 0, 0, 0, 0, 4, 1, 9, 0, 0, 5, 0, 0, 0, 0, 8, 0, 0, 7, 9},
			[]Grid{
				Grid{3, 4, 5, 6, 7, 8, 9, 1, 2, 6, 7, 2, 1, 9, 5, 3, 4, 8, 1, 9, 8, 3, 4, 2, 5, 6, 7, 8, 5, 9, 7, 6, 1, 4, 2, 3, 4, 2, 6, 8, 5, 3, 7, 9, 1, 7, 1, 3, 9, 2, 4, 8, 5, 6, 9, 6, 1, 5, 3, 7, 2, 8, 4, 2, 8, 7, 4, 1, 9, 6, 3, 5, 5, 3, 4, 2, 8, 6, 1, 7, 9},
				Grid{5, 3, 4, 6, 7, 8, 9, 1, 2, 6, 7, 2, 1, 9, 5, 3, 4, 8, 1, 9, 8, 3, 4, 2, 5, 6, 7, 8, 5, 9, 7, 6, 1, 4, 2, 3, 4, 2, 6, 8, 5, 3, 7, 9, 1, 7, 1, 3, 9, 2, 4, 8, 5, 6, 9, 6, 1, 5, 3, 7, 2, 8, 4, 2, 8, 7, 4, 1, 9, 6, 3, 5, 3, 4, 5, 2, 8, 6, 1, 7, 9},
			},
		},
		// no solution, input broken
		{
			Grid{1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0},
			[]Grid{},
		},
	}

	for _, test := range tests {
		got := Solve(&test.input)
		if len(got) != len(test.want) {
			t.Errorf("%v: expected %d solution(s), got %d", test.input, len(test.want), len(got))
			continue
		}
		for i, g := range got {
			w := test.want[i]
			if g != w {
				t.Errorf("%v: #%d: got %v, want %v", test.input, i, g, w)
			}
		}
	}
}

func loadPuzzles() ([]Grid, error) {
	grids := make([]Grid, 0, 95)

	file, err := os.Open("../../samples/95_hard_puzzles")
	if err != nil {
		return grids, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := scanner.Text()
		grid, err := NewGridFromString(line)
		if err != nil {
			return grids, err
		}
		grids = append(grids, grid)
	}

	if err := scanner.Err(); err != nil {
		return grids, err
	}

	return grids, nil
}

func BenchmarkSolve(b *testing.B) {
	grids, err := loadPuzzles()
	if err != nil {
		b.Errorf("failed to load grids: %s", err)
		return
	}
	for n := 0; n < b.N; n++ {
		grid := grids[n%len(grids)]
		Solve(&grid)
	}
}
