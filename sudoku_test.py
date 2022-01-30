import unittest

from logzero import logger  # type: ignore

from project_io import IO
from sudoku import Sudoku, SIZE


class TestSudoku(unittest.TestCase):
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
