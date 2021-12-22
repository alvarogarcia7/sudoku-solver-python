import unittest
from itertools import chain
from typing import List


class Sudoku:
    def __init__(self, value):
        assert len(value) == 9
        assert len(value[0]) == 9

        self.value = value


class IO:
    def load(self, raw_values):
        x: list[list[int]] = [list(map(lambda x: int(x), raw_value)) for raw_value in raw_values]
        return Sudoku(x)

    def serialize(self, sudoku: Sudoku):
        x: list[str] = ["".join(map(lambda x: x.__str__(), raw_value)) for raw_value in sudoku.value]
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


if __name__ == '__main__':
    unittest.main()
