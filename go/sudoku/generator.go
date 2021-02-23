package sudoku

import (
	"math/bits"
	"math/rand"
)

// randomValue returns the index of a bit randomly chosen in a bitmask.
// At least one bit must be set in choices, else randomValue panics.
func randomValue(choices uint16) uint8 {
	// Final value will be the position the n-th (0-indexed)
	// least significant bit set to 1 in the choices bitmask.
	n := rand.Intn(bits.OnesCount16(choices))
	for i := 0; i < n; i++ {
		// Set least significant bit to 0.
		choices &= choices - uint16(1)
	}
	// Find position of least significant bit.
	return uint8(bits.TrailingZeros16(choices))
}

// randomGrid creates a solution i.e. a valid, complete grid.
func randomGrid() Grid {
	for {
		var s solver
		s.init()
		// Fill cells with random values until the grid is complete.
		for _, cell := range rand.Perm(81) {
			if s.grid[cell] != 0 {
				continue
			}
			// Swap bits so 1 indicates "choice" rather than "conflict".
			choices := s.conflicts[cell] ^ conflict
			value := randomValue(choices)
			if !s.mark(cell, value) {
				break
			}
		}
		// If all cells were filled succesfully, the grid is valid.
		if s.progress == 81 {
			return s.grid
		}
	}
}

// minimize turns a solution into a problem by removing values from cells.
func (g *Grid) minimize() float64 {
	var value uint8
	var difficulty float64

	// Clear cells until this creates multiple solutions.
	for _, cell := range rand.Perm(81) {
		g[cell], value = uint8(0), g[cell]
		var s solver
		var grids []Grid
		s.init()
		if !s.load(g) {
			panic("minimize expects a valid grid")
		}
		grids = s.search(grids, false)
		if len(grids) == 0 {
			panic("minimize expects a valid grid")
		} else if len(grids) == 1 {
			// Only one solution was found.
			difficulty = s.difficulty()
		} else {
			// More than one solution was found, restore cell.
			g[cell] = value
		}
	}

	return difficulty
}

// Generate creates a random problem.
func Generate() (Grid, float64) {
	grid := randomGrid()
	difficulty := grid.minimize()
	return grid, difficulty
}
