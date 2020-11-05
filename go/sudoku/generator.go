package sudoku

import (
	"math/bits"
	"math/rand"
)

func randomOrder() [81]int {
	var order [81]int
	for i := range order {
		order[i] = i
	}
	rand.Shuffle(
		len(order),
		func(i int, j int) { order[i], order[j] = order[j], order[i] },
	)
	return order
}

func randomValue(choices uint16) uint8 {
	// Final value will be the position the n-th (0-indexed)
	// least significant bit set to 1 in the choices bitmask
	n := rand.Intn(bits.OnesCount16(choices))
	for i := 0; i < n; i++ {
		// Set least significant bit to 0
		choices &= choices - uint16(1)
	}
	// Find position of least significant bit
	return uint8(bits.TrailingZeros16(choices))
}

func randomGrid() Grid {
	for {
		var s solver
		// Fill cells with random values until the grid is complete
		for _, cell := range randomOrder() {
			if s.grid[cell] != 0 {
				continue
			}
			// Swap bits so 1 indicates "choice" rather than "conflict"
			choices := s.conflicts[cell] ^ conflict
			value := randomValue(choices)
			if !s.mark(cell, value) {
				break
			}
		}
		// Solver increments progress only when mark succeeds
		if s.progress < 81 {
			continue
		}
		return s.grid
	}
}

func minimize(g Grid) Grid {
	// g is a Grid rather than a *Grid because
	var value uint8
	// Clear cells until this creates multiple solutions
	for _, cell := range randomOrder() {
		g[cell], value = uint8(0), g[cell]
		var s solver
		var grids []Grid
		if !s.load(&g) {
			panic("minimize expects a valid grid")
		}
		grids = s.search(grids)
		if len(grids) == 0 {
			panic("minimize expects a valid grid")
		}
		if len(grids) > 1 {
			g[cell] = value
		}
	}
	return g
}

func Generate() Grid {
	grid := randomGrid()
	grid = minimize(grid)
	return grid
}
