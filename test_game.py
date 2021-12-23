import collections
import unittest
from typing import List, Optional, Any

SIZE: int = 9

consume = collections.deque(maxlen=0).extend


class Sudoku:
    def __init__(self, value):
        assert len(value) == 9
        assert len(value[0]) == 9

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

    def is_correct(self):
        try:
            return all([sorted(row) == list(range(1, 10)) for row in self.value])
        except TypeError:
            return False

    def solve(self):
        self._compute_candidate()
        # self.print_candidates()
        while (self._occupied_cells() != SIZE * SIZE):
            for value_candidate in range(0, SIZE):
                for row in range(0, SIZE):
                    for column in range(0, SIZE):
                        value_ = self.value[row][column]
                        if value_ is not None:
                            continue
                        by_row = set(filter(lambda i: [i, column] if self._is_empty[value_candidate][i][column] else None, range(0, SIZE)))
                        by_column = set(filter(lambda i: [row, i] if self._is_empty[value_candidate][row][i] else None, range(0, SIZE)))
                        by_square_positions = [[i, j] for i in range(row - row % 3, row - row % 3 + 3) for j in range(column - column % 3, column - column % 3 + 3)]
                        by_square = list(filter(lambda position: position if self._is_empty[value_candidate][position[0]][position[1]] else None, by_square_positions))
                        if len(by_row) == 1 and len(by_column) == 1 and len(by_square) == 1:
                            self.value[by_square[0][0]][by_square[0][1]] = value_candidate + 1
                            self._compute_candidate()

                        if len(by_square) == 1:
                            self.value[by_square[0][0]][by_square[0][1]] = value_candidate + 1
                            self._compute_candidate()


    def print_candidates(self):
        for value_0 in range(0, SIZE):
            print("")
            print(f"Candidates for {value_0 + 1}:")
            for row in range(0, SIZE):
                for column in range(0, SIZE):
                    print(f"{'X' if self._is_empty[value_0][row][column] else ' '} ", end="")
                    if column == 2 or column == 5:
                        print("| ", end="")
                print("")
                if row == 2 or row == 5:
                    print("- - - + - - - + - - -")

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


class IO:
    def load(self, raw_values):
        x: list[list[int]] = [list(map(lambda x: int(x) if x != ' ' else None, raw_value)) for raw_value in raw_values]
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
            "156789123",
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


if __name__ == '__main__':
    unittest.main()
