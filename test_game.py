import collections
import string
import unittest
from logzero import logger
from functools import reduce
from operator import and_

from typing import List, Optional, Any

SIZE: int = 9

consume = collections.deque(maxlen=0).extend


class Sudoku:
    def __init__(self, value):
        assert len(value) == 9
        # https://stackoverflow.com/questions/35429478/testing-and-assertion-in-list-comprehension
        assert reduce(and_, [len(row) == 9 for row in value])

        self.value = value
        # value (0_based) -> row -> column
        self._is_empty: list[list[list[bool]]] = self._empty_candidates()

    def _occupied_cells(self):
        result = 0
        for row in range(0, SIZE):
            for column in range(0, SIZE):
                if self.value[row][column] is not None:
                    result += 1
        return result

    def is_complete(self):
        return all([len(list(filter(lambda cell: cell is not None, row))) == 9 for row in self.value])

    @staticmethod
    def _square_for(row, column):
        x = row // 3
        y = column // 3
        return x * 3 + y

    def is_correct(self):
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

    def solve(self):
        if not self.is_correct():
            return
        self._compute_candidate()
        self._deduce_candidates()
        if self._occupied_cells() == SIZE * SIZE:
            return

        logger.debug(f"After deducing: {self._occupied_cells()} elements")
        # self.print_candidates(range(2, 3))

        # logger.debug(f"Start backtracking:")
        # self._apply_oracle_choice({'position': [1, 4], 'value': 2})
        # self._apply_oracle_choice({'position': [0, 6], 'value': 5})
        # self._apply_oracle_choice({'position': [5, 4], 'value': 1})
        # self._apply_oracle_choice({'position': [5, 1], 'value': 3})
        # self._apply_oracle_choice({'position': [5, 6], 'value': 9})
        # self._apply_oracle_choice({'position': [2, 5], 'value': 1})
        # self._apply_oracle_choice({'position': [3, 7], 'value': 6})
        self._compute_candidate()
        self._deduce_candidates()
        self.print_values("Before start backtracking")

        self.solve_r()

        self.print_values("After backtracking")
        # self.print_candidates()

    def solve_r(self) -> bool:
        if self.is_correct() and self._occupied_cells() == SIZE * SIZE:
            return True
        self._compute_candidate()
        choices = self._choices()
        for choice in choices:
            aux = self._copy()
            self.value[choice['position'][0]][choice['position'][1]] = choice['value']
            self._compute_candidate()
            self._deduce_candidates()
            if self.solve_r():
                return True
            self._copy_from(aux)

        return False
        # logger.debug(f"Still correct? {self.is_correct()}")

    def _deduce_candidates(self):
        assert (self.is_correct())
        while self._occupied_cells() != SIZE * SIZE:
            filled_this_iteration: bool = False
            for value_candidate in range(0, SIZE):
                for row in range(0, SIZE):
                    for column in range(0, SIZE):
                        value_ = self.value[row][column]
                        if value_ is not None:
                            continue
                        filled_this_iteration |= self._fill_candidate_in(column, row, value_candidate)
            if not filled_this_iteration:
                break

    def _fill_candidate_in(self, column, row, value_candidate):
        filled_this_iteration = False
        by_row = list(
            filter(lambda i: [i, column] if self._is_empty[value_candidate][i][column] else None, range(0, SIZE)))
        by_column = list(
            filter(lambda i: [row, i] if self._is_empty[value_candidate][row][i] else None, range(0, SIZE)))
        by_square_positions = [[i, j] for i in range(row - row % 3, row - row % 3 + 3) for j in
                               range(column - column % 3, column - column % 3 + 3)]
        by_square = list(
            filter(lambda position: position if self._is_empty[value_candidate][position[0]][position[1]] else None,
                   by_square_positions))
        if len(by_row) == 1 and len(by_column) == 1 and len(by_square) == 1:
            self.value[by_square[0][0]][by_square[0][1]] = value_candidate + 1
            self._compute_candidate()
            filled_this_iteration = True
        if len(by_square) == 1:
            self.value[by_square[0][0]][by_square[0][1]] = value_candidate + 1
            self._compute_candidate()
            filled_this_iteration = True
        return filled_this_iteration

    def print_candidates(self, value_0_range=range(0, SIZE), function=logger.debug):
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
        # [[list(range(0,3)) for row in range(0,9)] for column in range(0,3) for value in range(0,3)] ??
        result: list[list[list[bool]]] = []
        for cell_value in range(0, SIZE):
            this_value = []
            for row_value in range(0, SIZE):
                row = []
                for column_value in range(0, SIZE):
                    row.append(True)
                this_value.append(row)
            result.append(this_value)
        return result

    def __set_occupied(self, row, column, value_0):
        self._is_empty[value_0][row][column] = False

    def _compute_candidate(self):
        self._is_empty = self._empty_candidates()
        for row_value in range(0, SIZE):
            for column_value in range(0, SIZE):
                value_ = self.value[row_value][column_value]
                if value_ is None:
                    continue
                value_0 = value_ - 1
                consume(self.__set_occupied(row_value, column_value, value_0) for value_0 in range(0, SIZE))
                consume(self.__set_occupied(row_value, column_value, value_0) for row_value in range(0, SIZE))
                consume(self.__set_occupied(row_value, column_value, value_0) for column_value in range(0, SIZE))
                self.__set_occupied_square(row_value, column_value, value_0)

    def __set_occupied_square(self, row_value: int, column_value: int, value_0: int):
        square_row_begin = row_value - row_value % 3
        square_column_begin = column_value - column_value % 3
        for row_value in range(square_row_begin, square_row_begin + 2 + 1):
            for column_value in range(square_column_begin, square_column_begin + 2 + 1):
                self.__set_occupied(row_value, column_value, value_0)

    def print_values(self, message: string, function=logger.info):
        function(f"{message}: is correct? {self.is_correct().__str__()}")
        self._print_values(function)

    def _print_values(self, function):
        for row in range(0, SIZE):
            row_text: list = []
            for column in range(0, SIZE):
                row_text.append(f"{self.value[row][column] if self.value[row][column] is not None else ' '} ")
                if column == 2 or column == 5:
                    row_text.append("| ")
            function("".join(row_text))
            if row == 2 or row == 5:
                function("- - - + - - - + - - -")

    def _choices(self):
        min_ocurrences = 9
        selected_positions: list[[int, int]] = []
        for value_0 in range(SIZE):
            # column with the least candidates
            for row in range(0, SIZE):
                current_positions: list[[int, int]] = []
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

    def _copy(self) -> list[list[int]]:
        result = []
        for row in self.value:
            result.append(row.copy())
        return result

    def _copy_from(self, aux) -> None:
        self.value = []
        for row in aux:
            self.value.append(row.copy())
        self._compute_candidate()

    def _apply_oracle_choice(self, param):
        self.value[param['position'][0]][param['position'][1]] = param['value']  # Oracle


class IO:
    def load(self, raw_values):
        x: list[list[int]] = [list(map(lambda x: int(x) if x != ' ' and x != '.' else None, raw_value)) for raw_value in
                              raw_values]
        return Sudoku(x)

    def serialize(self, sudoku: Sudoku):
        x: list[str] = ["".join(map(lambda x: x.__str__() if x is not None else ' ', raw_value)) for raw_value in
                        sudoku.value]
        return x


class TestIOTest(unittest.TestCase):
    def test_roundtrip_loading(self):
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

    def test_roundtrip_loading_when_not_complete(self):
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

    def test_check_is_complete(self):
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

    def test_check_is_incomplete(self):
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

    def test_check_is_correct(self):
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

    def test_check_is_correct(self):
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

    def test_check_is_correct_while_incomplete(self):
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

    def test_check_is_not_correct_while_incomplete_in_column(self):
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

    def test_check_is_not_correct_while_incomplete_in_row(self):
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

    def test_check_is_not_correct_while_incomplete_in_square(self):
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

    def test_complete_simple_without_ambiguity(self):
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

    def test_find_square(self):
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

    def test_complete_simple_without_ambiguity_2(self):
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

    def test_complete_simple_without_ambiguity_3(self):
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

    def test_complete_sudoku_with_ambiguity(self):
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

    def test_fail_to_complete_impossible_sudoku(self):
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
