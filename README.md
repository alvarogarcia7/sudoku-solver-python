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


## Performance work

### Process

1. Create a baseline measurement (no optimisation). Automatically print the results (python code) when executing the performance test.
2. Profile the code.
3. Compute statistical tests (mean, standard deviation). Assume a measurement is relevant if improves three sigmas (see code).
4. Create a commit with the improvement percentage (write down if this improvement was statistically significant; even if it doesn't, any improvement is introduced).
Revert commits that introduce negative performance changes (i.e., worsening performance)
5. Manually update baseline (i.e., copy-paste output from performance test to python code.)
6. Repeat.

Notes:

1. Keep a performance test (longer, with baseline) and a timing test (short, with timer too) to debug, profile, etc.
Do not use timing while debugging (even without breakpoints), as this is slower and altering the execution environment. 
2. (Python-specific) Use `timeit.repeat` to get X measurements (so you can perform the statistics) instead of `timeit.time` (that computes the mean for you)

### Results

For the final measurements, this environment was used:

```
MacOS, 2.4 GHz 8-Core Intel Core i9, 32GB 2667 MHz DDR4
On-the-host (not virtualised)
Python 3.9.5 (default, May  4 2021, 03:33:11) 
[Clang 12.0.0 (clang-1200.0.32.29)] on darwin
```

This optimisation improves by 62% the previous result.