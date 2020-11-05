package sudoku

import (
	"math/rand"
	"testing"
)

func TestGenerate(t *testing.T) {
	for seed := 0; seed < 5; seed++ {
		rand.Seed(42 << seed)
		grid := Generate()
		solutions := Solve(&grid)
		if len(solutions) != 1 {
			t.Errorf("seed = %d: more than one solution", seed)
		}
	}
}
