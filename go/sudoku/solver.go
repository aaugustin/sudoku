package sudoku

import (
	"math"
	"math/bits"
)

var relations [81][20]int

func init() {
	// Precompute relation map — this takes about 16µs, which is fine
	for i1 := 0; i1 < 9; i1++ {
		for j1 := 0; j1 < 9; j1++ {
			i := 0
			for i2 := 0; i2 < 9; i2++ {
				for j2 := 0; j2 < 9; j2++ {
					if (i1 == i2) != (j1 == j2) ||
						// i1 != i2 implies j1 != j2 at this point
						(i1/3 == i2/3 && j1/3 == j2/3 && i1 != i2) {
						relations[9*i1+j1][i] = 9*i2 + j2
						i++
					}
				}
			}
		}
	}
}

const conflict uint16 = (1 << 10) - (1 << 1) // set bits 1 to 9

// solver implements the Sudoku solving algorithm.
//
// Using a solver properly takes three steps.
// First, call init. This brings significant performance benefits.
// Second, call mark for each cell whose value is known.
// Third, call search to look for solutions.
type solver struct {
	next      []int
	steps     int
	progress  uint8
	grid      Grid
	conflicts [81]uint16 // bitmask - uses bits 1 to 9 out of 16
}

// init optimizes the performance of a solver by pre-allocating memory.
func (s *solver) init() {
	// Allocate memory only once instead of growing the slice incrementally.
	if s.next != nil {
		panic("must init only once")
	}
	s.next = make([]int, 0, 81)
}

// load marks all cells whose value is known.
//
// The return value is the same as in mark.
func (s *solver) load(grid *Grid) bool {
	for cell, value := range grid {
		if value == 0 {
			continue
		}
		if !s.mark(cell, value) {
			return false
		}
	}
	return true
}

// mark attempts to set the value of a cell.
//
// If the value could be set, mark returns true. This doesn't imply that
// the problem has at least a solution.
//
// If the value couldn't be set without breaking the rules, mark returns
// false. This makes the solver unusable. It must be discarded.
func (s *solver) mark(cell int, value uint8) bool {
	// If this value is already known, there's nothing to do.
	// This happens if the input is over-constrained.
	if s.grid[cell] == value {
		return true
	}

	// If we hit an incompatibility, this value doesn't work.
	if s.conflicts[cell]&(1<<value) != 0 {
		return false
	}

	// Assign value.
	s.conflicts[cell] = conflict
	s.grid[cell] = value
	s.steps++

	// Apply constraints.
	for _, related := range relations[cell] {
		// If the constraint was already known, move on.
		if s.conflicts[related]&(1<<value) != 0 {
			continue
		}
		// Record the constraint.
		s.conflicts[related] |= 1 << value
		// If we create an incompatibility, this value doesn't work.
		if s.conflicts[related] == conflict {
			return false
		}
		// If we can determine the value, add it to the queue.
		if bits.OnesCount16(s.conflicts[related]) == 8 {
			s.next = append(s.next, related)
		}
	}

	// If new values become known, mark them recursively.
	for len(s.next) > 0 {
		cell, s.next = s.next[0], s.next[1:]
		value = uint8(bits.TrailingZeros16(s.conflicts[cell] ^ conflict))
		if !s.mark(cell, value) {
			return false
		}
	}

	// No incompatibility was found.
	s.progress++
	return true
}

// search finds all solutions.
//
// It appends solutions to the grids slice and returns that slice.
//
// When multiple is false, search aborts as soon as two solutions are found.
// This is useful to know whether there's zero, one, or several solutions.
// When multiple is true, it looks for all solutions.
func (s *solver) search(grids []Grid, multiple bool) []Grid {
	// If the grid is complete, there is a solution in this branch.
	if s.progress == 81 {
		grids = append(grids, s.grid)
		return grids
	}

	// Since s.next is empty, sharing the underlying array with a copy is OK.
	// Indeed, mark() only pushes next steps in the queue and then pops them.
	// Since search() explores options sequentially, reusing the same memory
	// space for next steps doesn't cause problems.
	if len(s.next) > 0 {
		panic("must process next before searching")
	}

	// Try all possible values of the cell with the fewest choices.
	var copy solver
	cell := s.candidate()
	for value := uint8(1); value < uint8(10); value++ {
		if s.conflicts[cell]&(1<<value) == 0 {
			copy = *s
			if copy.mark(cell, value) {
				grids = copy.search(grids, multiple)
				// Abort search when two solutions are found and we don't look for more.
				if !multiple && len(grids) > 1 {
					s.steps = copy.steps
					break
				}
			}
			s.steps = copy.steps
		}
	}
	return grids
}

// candidate find the cell with the most conflicts.
//
// This minimizes how many paths the solver has to explore to find all solutions.
func (s *solver) candidate() int {
	candidate := 0
	score := 0
	for cell, value := range s.grid {
		if value == 0 {
			conflicts := bits.OnesCount16(s.conflicts[cell])
			if conflicts > score {
				// candidate() runs when all empty cells have at least 2 choices i.e. at
				// most 7 conflicts. Stop searching if we find a cell with 7 conflicts.
				if conflicts >= 7 {
					return cell
				}
				candidate = cell
				score = conflicts
			}
		}
	}
	return candidate
}

// difficulty estimates how difficult the grid is.
//
// The value usually rounds down to an integer between 1 and 5, making it
// suitable for a rating. 6 or more is possible but uncommon.
func (s *solver) difficulty() float64 {
	return math.Log(math.Max(float64(s.steps)/81, 1)) + 1
}

// Solve a grid.
//
// Return a slice of 0, 1, or several solutions, and an estimate of how
// difficult the grid is.
//
// When multiple is false and there are multiple solutions, stop searching as
// soon as two solutions are found.
func Solve(g *Grid, multiple bool) ([]Grid, float64) {
	var s solver
	var grids []Grid
	s.init()
	if s.load(g) {
		grids = s.search(grids, multiple)
	}
	return grids, s.difficulty()
}
