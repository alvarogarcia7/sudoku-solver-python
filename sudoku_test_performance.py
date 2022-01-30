import timeit
from statistics import mean, stdev

from project_io import IO


def test_performance_ambiguity_49() -> None:
    # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/easy49.sud
    raw_values = [
        ".....3.17",
        ".15..9..8",
        ".6.......",
        "1....7...",
        "..9...2..",
        "...5....4",
        ".......2.",
        "5..6..34.",
        "34.2....."
    ]
    io = IO()
    current_results = timeit.repeat(
        setup='''sudoku = io.load(raw_values)''',
        stmt='''
sudoku.solve()
assert(sudoku.is_correct())
assert(sudoku.is_complete())
''',
        repeat=10, number=1,
        globals={'io': io, 'raw_values': raw_values})
    print(f"best_previous_results = {current_results}")

    best_previous_results = [1.3065322620000002, 1.2987408720000002, 1.2974850990000002, 1.3091255469999998,
                             1.2975625549999998, 1.3031685460000002, 1.308674904, 1.297135106999999,
                             1.325483780999999, 1.3021483840000005]
    lower_end = mean(best_previous_results) - 3 * stdev(best_previous_results)

    difference_in_percentage = (1 - mean(current_results) / mean(best_previous_results)) * 100
    is_positive: bool = difference_in_percentage > 0
    print(
        f"This optimisation {'improves' if is_positive else 'is worse'} by {abs(round(difference_in_percentage, None))}%")

    # self.assertTrue(mean(current_results) < lower_end, msg="This optimisation is not statistically significant")