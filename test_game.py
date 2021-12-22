import unittest
from itertools import chain
from typing import List


class Sudoku:
    def __init__(self, value):
        assert len(value) == 9
        assert len(value[0]) == 9

        self.value = value

    def is_complete(self):
        return all([len(list(filter(lambda cell: cell is not None, row))) == 9 for row in self.value])


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

        self.assertTrue(sudoku.is_complete())


if __name__ == '__main__':
    unittest.main()
