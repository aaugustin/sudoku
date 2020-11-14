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
func (g *Grid) minimize() {
	var value uint8
	var solved bool
	// Clear cells until this creates multiple solutions.
	for _, cell := range rand.Perm(81) {
		g[cell], value = uint8(0), g[cell]
		solved = false
		if !g.solve(func(_ *Grid) bool {
			// Another solution was already found, abort.
			if solved {
				return false
			}
			// First solution is found, continue.
			solved = true
			return true
		}) {
			// More than one solution was found, restore cell.
			g[cell] = value
		}
		if !solved {
			panic("minimize expects a valid grid")
		}
	}
}

// Generate creates a random problem.
func Generate() Grid {
	grid := randomGrid()
	grid.minimize()
	return grid
}
