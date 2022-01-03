# Sudoku Solver

This is an étude to practice backtracking, algorithms.

Goal: solve a sudoku given its initial state.

See also a similar étude in C.

Iterations:

1. Solver using 'deducing' numbers. This strategy does not allow for ambiguity / nondeterminism. Non-ambiguous sudokus can be solved with a greedy algorithm.
2. Solver using 'backtracking' to try alternatives when there is ambiguity. Naive implementation, disregarding performance
3. Optimise performance for the backtracking iteration.
4. [Pending] Use Knuth's Dancing Links X (DLX) as an alternative to backtracking.
5. [Pending] Compare 'DLX' and 'backtracking' alternatives
6. [Pending] Find better heuristics for all alternatives (improving the runtime due to a better algorithm)


### Results

For the final measurements, this environment was used:

```
MacOS, 2.4 GHz 8-Core Intel Core i9, 32GB 2667 MHz DDR4
On-the-host (not virtualised)
Python 3.9.5 (default, May  4 2021, 03:33:11) 
[Clang 12.0.0 (clang-1200.0.32.29)] on darwin
```

This optimisation improves by 62% the previous result.