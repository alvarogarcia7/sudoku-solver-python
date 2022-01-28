import functools
import timeit
import unittest
from typing import List, Dict, Union, Optional, Callable, TypedDict, Any

from logzero import logger  # type: ignore
from functools import reduce
from operator import and_
from statistics import mean, stdev

SIZE: int = 9

Choice = TypedDict('Choice', {'position': List[int], 'value': int})


class Sudoku:
    def __init__(self, value: List[List[Optional[int]]]):
        assert len(value) == 9
        # https://stackoverflow.com/questions/35429478/testing-and-assertion-in-list-comprehension
        assert reduce(and_, [len(row) == 9 for row in value])

        self.value = value
        # value (0_based) -> row -> column
        self._is_empty: list[list[list[bool]]] = self._empty_candidates()

    @functools.cache
    def cells_for_square_at(self, row: int, column: int) -> List[List[int]]:
        return [[i, j] for i in range(row - row % 3, row - row % 3 + 3) for j in
                range(column - column % 3, column - column % 3 + 3)]

    def _occupied_cells(self) -> int:
        result = 0
        for row in range(0, SIZE):
            for column in range(0, SIZE):
                if self.value[row][column] is not None:
                    result += 1
        return result

    def is_complete(self) -> bool:
        return all([len(list(filter(lambda cell: cell is not None, row))) == 9 for row in self.value])

    @staticmethod
    @functools.cache
    def _square_for(row: int, column: int) -> int:
        x = row // 3
        y = column // 3
        return x * 3 + y

    def is_correct(self) -> bool:
        frequency_column: list[list[int]] = [[0 for _ in range(9)] for _ in range(9)]
        frequency_square: list[list[int]] = [[0 for _ in range(9)] for _ in range(9)]
        frequency_row: list[list[int]] = [[0 for _ in range(9)] for _ in range(9)]
        for row in range(0, SIZE):
            for column in range(0, SIZE):
                value_optional = self.value[row][column]
                if value_optional is None: continue
                value_0 = value_optional - 1
                frequency_row[row][value_0] += 1
                frequency_column[column][value_0] += 1
                frequency_square[Sudoku._square_for(row, column)][value_0] += 1

        for i in range(0, len(frequency_row)):
            for value_0 in range(0, SIZE):
                if frequency_row[i][value_0] > 1:
                    # logger.debug(f"Repeated element {value_0 + 1} in row {i}")
                    return False

        for i in range(0, len(frequency_column)):
            for value_0 in range(0, SIZE):
                if frequency_column[i][value_0] > 1:
                    # logger.debug(f"Repeated element {value_0 + 1} in column {i}")
                    return False

        for i in range(0, len(frequency_square)):
            for value_0 in range(0, SIZE):
                if frequency_square[i][value_0] > 1:
                    # logger.debug(f"Repeated element {value_0 + 1} in square {i}")
                    return False

        return True

    def solve(self) -> None:
        if not self.is_correct():
            return
        self._compute_candidate()
        self._deduce_candidates()
        if self._occupied_cells() == SIZE * SIZE:
            return

        # logger.debug(f"After deducing: {self._occupied_cells()} elements")
        # self.print_values("Before start backtracking")

        self.solve_r()

        # self.print_values("After backtracking")

    def solve_r(self) -> bool:
        if self.is_correct() and self._occupied_cells() == SIZE * SIZE:
            return True
        self._compute_candidate()
        choice: Choice
        for choice in self._choices():
            aux = self._copy()
            self._position(choice['position'][0], choice['position'][1], choice['value'])
            self._deduce_candidates()
            if self.solve_r():
                return True
            self._copy_from(aux)

        return False
        # logger.debug(f"Still correct? {self.is_correct()}")

    def _deduce_candidates(self) -> None:
        assert (self.is_correct())
        frequency_number: list[int] = [0 for _ in range(9)]
        for row in range(0, SIZE):
            for column in range(0, SIZE):
                value_optional = self.value[row][column]
                if value_optional is None: continue
                value_0 = value_optional - 1
                frequency_number[value_0] += 1

        while True:
            filled_this_iteration: bool = False
            for value_candidate in range(0, SIZE):
                if frequency_number[value_candidate] == SIZE: continue
                for row in range(0, SIZE):
                    for column in range(0, SIZE):
                        value_ = self.value[row][column]
                        if value_ is not None:
                            continue
                        filled_this_iteration |= self._fill_candidate_in(column, row, value_candidate)
            if not filled_this_iteration:
                break

    def _fill_candidate_in(self, column: int, row: int, value_candidate: int) -> bool:
        by_square_positions = self.cells_for_square_at(row, column)
        by_square = list(
            filter(lambda position: position if self._is_empty[value_candidate][position[0]][position[1]] else None,
                   by_square_positions))
        if len(by_square) == 1:
            self._position(by_square[0][0], by_square[0][1], value_candidate + 1)
            return True
        return False

    def print_candidates(self, value_0_range: range = range(0, SIZE),
                         function: Callable[[str], None] = logger.debug) -> None:
        for value_0 in value_0_range:
            function(f"Candidates for {value_0 + 1}:")
            for row in range(0, SIZE):
                row_text = []
                for column in range(0, SIZE):
                    row_text.append(f"{'X' if self._is_empty[value_0][row][column] else ' '} ")
                    if column == 2 or column == 5:
                        row_text.append("| ")
                function("".join(row_text))
                if row == 2 or row == 5:
                    function("- - - + - - - + - - -")

    @staticmethod
    def _empty_candidates() -> list[list[list[bool]]]:
        result: list[list[list[bool]]] = [
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ],
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ],
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ],
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ],
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ],
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ],
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ],
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ],
            [
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True],
                [True, True, True, True, True, True, True, True, True]
            ]
        ]
        return result

    def _compute_candidate(self) -> None:
        self._is_empty = self._empty_candidates()
        for row_value in range(0, SIZE):
            for column_value in range(0, SIZE):
                value_ = self.value[row_value][column_value]
                if value_ is None:
                    continue
                value_0 = value_ - 1
                for i in range(0, SIZE):
                    self._is_empty[value_0][i][column_value] = False
                    self._is_empty[value_0][row_value][i] = False
                    self._is_empty[i][row_value][column_value] = False
                self.__set_occupied_square(row_value, column_value, value_0)

    def _compute_candidate_partial(self, row: int, column: int, value_0: int) -> None:
        for i in range(0, SIZE):
            self._is_empty[value_0][i][column] = False
            self._is_empty[value_0][row][i] = False
            self._is_empty[i][row][column] = False
        self.__set_occupied_square(row, column, value_0)

    def __set_occupied_square(self, row_value: int, column_value: int, value_0: int) -> None:
        for [row_value, column_value] in self.cells_for_square_at(row_value, column_value):
            self._is_empty[value_0][row_value][column_value] = False

    def print_values(self, message: str, function: Callable[[str], None] = logger.info) -> None:
        function(f"{message}: is correct? {self.is_correct().__str__()}")
        self._print_values(function)

    def _print_values(self, function: Callable[[str], None]) -> None:
        for row in range(0, SIZE):
            row_text: list[str] = []
            for column in range(0, SIZE):
                row_text.append(f"{self.value[row][column] if self.value[row][column] is not None else ' '} ")
                if column == 2 or column == 5:
                    row_text.append("| ")
            function("".join(row_text))
            if row == 2 or row == 5:
                function("- - - + - - - + - - -")

    def _choices(self) -> list[Choice]:
        min_ocurrences = 9
        selected_positions: List[Any] = []
        for value_0 in range(SIZE):
            # column with the least candidates
            for row in range(0, SIZE):
                current_positions: List[Any] = []
                current_occurrences = 0
                for column in range(0, SIZE):
                    if self._is_empty[value_0][row][column]:
                        current_occurrences += 1
                        current_positions.append({'position': [row, column], 'value': value_0 + 1})
                if 0 < current_occurrences < min_ocurrences:
                    min_ocurrences = current_occurrences
                    selected_positions = current_positions.copy()

        if selected_positions is not None:
            return selected_positions
        return []

    def _copy(self) -> list[list[Optional[int]]]:
        result = []
        for row in self.value:
            result.append(row.copy())
        return result

    def _copy_from(self, aux: List[List[Optional[int]]]) -> None:
        self.value = []
        for row in aux:
            self.value.append(row.copy())
        self._compute_candidate()

    def _position(self, row: int, column: int, value: int) -> None:
        self.value[row][column] = value
        self._compute_candidate_partial(row, column, value - 1)


class IO:
    def load(self, raw_values: List[str]) -> Sudoku:
        return Sudoku(self.load_generic(raw_values))

    def load_generic(self, raw_values: List[str]) -> List[List[Optional[int]]]:
        return [list(map(lambda x: int(x) if x != ' ' and x != '.' else None, raw_value)) for raw_value in
                raw_values]

    def serialize(self, sudoku: Sudoku) -> List[str]:
        return ["".join(map(lambda x: x.__str__() if x is not None else ' ', raw_value)) for raw_value in
                sudoku.value]


class TestIOTest(unittest.TestCase):
    def test_roundtrip_loading(self) -> None:
        io = IO()
        raw_values = [
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789"
        ]
        sudoku = io.load(raw_values)
        actual = io.serialize(sudoku)
        self.assertEqual(raw_values, actual)

    def test_roundtrip_loading_when_not_complete(self) -> None:
        io = IO()
        raw_values = [
            " 23456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789"
        ]
        sudoku = io.load(raw_values)
        actual = io.serialize(sudoku)
        self.assertEqual(raw_values, actual)

    def test_check_is_complete(self) -> None:
        raw_values = [
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789"
        ]
        sudoku = IO().load(raw_values)

        self.assertTrue(sudoku.is_complete())

    def test_check_is_incomplete(self) -> None:
        raw_values = [
            " 23456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789",
            "123456789"
        ]
        sudoku = IO().load(raw_values)

        self.assertFalse(sudoku.is_complete())

    def test_check_is_correct(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/solved1.sud
        raw_values = [
            "123456789",
            "456789123",
            "789123456",
            "214365897",
            "365897214",
            "897214365",
            "531642978",
            "642978531",
            "978531642"
        ]
        sudoku = IO().load(raw_values)

        self.assertTrue(sudoku.is_correct())

    def test_check_is_not_correct_with_repeated_element(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/solved1.sud
        raw_values = [
            "123456789",
            "156789123",  # repeated element 1
            "789123456",
            "214365897",
            "365897214",
            "897214365",
            "531642978",
            "642978531",
            "978531642"
        ]
        sudoku = IO().load(raw_values)

        self.assertFalse(sudoku.is_correct())

    def test_check_is_correct_while_incomplete(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/solved1.sud
        raw_values = [
            "1        ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         "
        ]
        sudoku = IO().load(raw_values)

        self.assertTrue(sudoku.is_correct())

    def test_check_is_not_correct_while_incomplete_in_column(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/solved1.sud
        raw_values = [
            "1        ",
            "1        ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         "
        ]
        sudoku = IO().load(raw_values)

        self.assertFalse(sudoku.is_correct())

    def test_check_is_not_correct_while_incomplete_in_row(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/solved1.sud
        raw_values = [
            "11       ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         "
        ]
        sudoku = IO().load(raw_values)

        self.assertFalse(sudoku.is_correct())

    def test_check_is_not_correct_while_incomplete_in_square(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/solved1.sud
        raw_values = [
            "1        ",
            "         ",
            "  1      ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         ",
            "         "
        ]
        sudoku = IO().load(raw_values)

        self.assertFalse(sudoku.is_correct())

    def test_complete_simple_without_ambiguity(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/solved1.sud
        raw_values = [
            "123456789",
            " 56789123",
            "789123456",
            "214365897",
            "36589721 ",
            "89721 365",
            "5 16 2978",
            "6 2978531",
            "978531642"
        ]
        sudoku = IO().load(raw_values)

        sudoku.solve()

        self.assertTrue(sudoku.is_correct())
        self.assertTrue(sudoku.is_complete())

    def test_find_square(self) -> None:
        map_square = [[0, 0, 0, 0, 0, 0, 0, 0, 0] for _ in range(0, SIZE)]

        for row in range(0, SIZE):
            for column in range(0, SIZE):
                map_square[row][column] = Sudoku._square_for(row, column)

        self.assertEqual(
            [[0, 0, 0, 1, 1, 1, 2, 2, 2],
             [0, 0, 0, 1, 1, 1, 2, 2, 2],
             [0, 0, 0, 1, 1, 1, 2, 2, 2],

             [3, 3, 3, 4, 4, 4, 5, 5, 5],
             [3, 3, 3, 4, 4, 4, 5, 5, 5],
             [3, 3, 3, 4, 4, 4, 5, 5, 5],

             [6, 6, 6, 7, 7, 7, 8, 8, 8],
             [6, 6, 6, 7, 7, 7, 8, 8, 8],
             [6, 6, 6, 7, 7, 7, 8, 8, 8]],
            map_square)

    def test_complete_simple_without_ambiguity_2(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/easy1.sud
        raw_values = [
            "  3 2 6  ",
            "9  3 5  1",
            "  18 64  ",
            "  81 29  ",
            "7       8",
            "  67 82  ",
            "  26 95  ",
            "8  2 3  9",
            "  5 1 3  ",
        ]
        sudoku = IO().load(raw_values)

        sudoku.solve()

        self.assertTrue(sudoku.is_correct())
        self.assertTrue(sudoku.is_complete())

    def test_complete_simple_without_ambiguity_3(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/easy2.sud
        raw_values = [
            "2   8 3  ",
            " 6  7  84",
            " 3 5  2 9",
            "   1 54 8",
            "         ",
            "4 27 6   ",
            "3 1  7 4 ",
            "72  4  6 ",
            "  4 1   3"
        ]
        sudoku = IO().load(raw_values)

        sudoku.solve()

        self.assertTrue(sudoku.is_correct())
        self.assertTrue(sudoku.is_complete())

    def test_complete_sudoku_with_ambiguity(self) -> None:
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
        sudoku = IO().load(raw_values)

        sudoku.solve()

        self.assertTrue(sudoku.is_correct())
        self.assertTrue(sudoku.is_complete())

    def test_performance_ambiguity_49(self) -> None:
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

    def test_fail_to_complete_impossible_sudoku(self) -> None:
        # Source: https://github.com/jimburton/sudoku/blob/master/puzzles/impossible.sud
        raw_values = [
            "36..712..",
            ".5....18.",
            "..92.47..",
            "....13.28",
            "4..1.2..9",
            "27.46....",
            "..53.89..",
            ".83....6.",
            "..769..43"
        ]
        sudoku = IO().load(raw_values)

        sudoku.solve()

        self.assertFalse(sudoku.is_correct())
        self.assertFalse(sudoku.is_complete())


if __name__ == '__main__':
    unittest.main()
