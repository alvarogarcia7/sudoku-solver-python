import unittest
from functools import reduce
from operator import and_
from typing import List, Any

from test_game import IO

SIZE: int = 9


class ExactCover:
    def __init__(self, value):
        # assert square matrix
        assert len(value) == len(value[0])
        # https://stackoverflow.com/questions/35429478/testing-and-assertion-in-list-comprehension
        assert reduce(and_, [len(row) == len(value[0]) for row in value])

        self.value = value

    def _constraint_matrix(self) -> dict[str, set[str]]:
        constraint_numbers = [[value, i, j] for value in range(1, 3) for i in range(1, 3) for j in range(1, 3)]

        constraints = {'some_in_column_and_row': set(),
                       'number_in_row': set(),
                       'number_in_column': []}
        for i in constraint_numbers:
            constraints['number_in_row'].add(f"{i[0]}_{i[1]}")
            constraints['some_in_column_and_row'].add(self.value_at(i[0], [i[1], i[2]]))
            constraints['number_in_column'].append(self.value_at(i[0], [i[1], i[2]]))

        return constraints

    @staticmethod
    def value_at(value: int, position: list[int]) -> str:
        return f"{value}_({position[0]},{position[1]})"

    def _choice_matrix(self):
        return [
            [[1, [1, 1]], [True, False, False, False], [True, False, False, False], [True, False, False, False]]
        ]

    @staticmethod
    def _s(x):
        if x:
            return 'X'
        return ""

    @classmethod
    def print_choice_matrix(cls, choice_matrix):
        print('{:8s} | {:10s} | {:11s} | {:11s}'.format('choice', 'some number', 'the number', 'the number'))
        print('{:8s} | {:5d} {:5d} | {:5d} {:5d} | {:4d} {:4d}'.format('', 1, 2, 1, 2, 1, 2))
        print('{:8s} | {:11s} | {:10s} | {:10s}'.format('', 'and row', 'must in row', 'must in col'))
        print(
            '{:8s} | {:2d} {:2d} {:2d} {:2d} | {:2d} {:2d} {:2d} {:2d} | {:2d} {:2d} {:2d} {:2d}'.format('', 1, 2, 1, 2,
                                                                                                         1,
                                                                                                         2, 1, 2,
                                                                                                         1, 2, 1, 2))

        for row in choice_matrix:
            print('{:d} @ ({:d},{:d})|'.format(row[0][0], row[0][1][0], row[0][1][1]), end="")
            for j in range(1, 4):
                for i in row[j]:
                    print('  {:1s}'.format(ExactCover._s(i)), end="")
                print(" |", end="")
            print()

        pass


class TestIOTest(unittest.TestCase):
    def test_generate_latin_square_2x2(self):
        raw_values = [
            "  ",
            "  "
        ]
        constraint_matrix = ExactCover(IO().load_generic(raw_values))._constraint_matrix()
        self.assertTrue(constraint_matrix['some_in_column_and_row'].__contains__(ExactCover.value_at(1, [1, 1])))
        self.assertTrue(constraint_matrix['some_in_column_and_row'].__contains__(ExactCover.value_at(2, [1, 1])))

        constraint_numbers = [[value, i, j] for value in range(1, 3) for i in range(1, 3) for j in range(1, 3)]
        # [1, 1, 1], [1, 1, 2], [1, 2, 1], [1, 2, 2], [2, 1, 1], [2, 1, 2], [2, 2, 1], [2, 2, 2]
        for row in constraint_numbers:
            self.assertTrue(
                constraint_matrix['some_in_column_and_row'].__contains__(ExactCover.value_at(row[0], [row[1], row[2]])))

        self.assertTrue(constraint_matrix['number_in_row'].__contains__(f"1_1"))

        self.assertEqual(8, len(constraint_matrix['some_in_column_and_row']))
        self.assertEqual(4, len(constraint_matrix['number_in_row']))
        self.assertEqual(8, len(constraint_matrix['number_in_column']))

    def test_generate_latin_square_2x2_2(self):
        raw_values = [
            "  ",
            "  "
        ]
        choice_matrix = ExactCover(IO().load_generic(raw_values))._choice_matrix()

        ExactCover.print_choice_matrix(choice_matrix)


if __name__ == '__main__':
    unittest.main()
