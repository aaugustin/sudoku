package sudoku

import (
	"math/rand"
	"testing"
)

func TestGenerate(t *testing.T) {
	for seed := 0; seed < 5; seed++ {
		rand.Seed(42 << seed)
		grid := Generate()

		// Most grids have between 55 and 60 zeroes
		zeroCount := 0
		for _, cell := range grid {
			if cell == 0 {
				zeroCount++
			}
		}
		if zeroCount < 50 || zeroCount > 65 {
			t.Errorf("seed = %d: expected between 50 and 65 zeroes, got %d", seed, zeroCount)
		}

		solutions := Solve(&grid)
		if len(solutions) != 1 {
			t.Errorf("seed = %d: more than one solution", seed)
		}
	}
}

func BenchmarkGenerate(b *testing.B) {
	for n := 0; n < b.N; n++ {
		rand.Seed(int64(42 * n))
		_ = Generate()
	}
}
