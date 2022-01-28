import copy
import unittest
from functools import reduce
from operator import and_
from typing import Dict, Union, Set, Any, List, TypedDict, Optional

from test_game import IO

SIZE: int = 9

Constraints = TypedDict('Constraints', {'some_in_column_and_row': Set[str],
                                        'number_in_row': Set[str],
                                        'number_in_column': List[str]})
ChoiceRow = TypedDict('ChoiceRow', {'choice': int, 'position': List[int], 'constraints': List[List[bool]]})


class ExactCover:
    def __init__(self, value: List[List[Optional[int]]]):
        # assert square matrix
        assert len(value) == len(value[0])
        # https://stackoverflow.com/questions/35429478/testing-and-assertion-in-list-comprehension
        assert reduce(and_, [len(row) == len(value[0]) for row in value])

        self.range = range(1, 2 + 1)

        self.choice_matrix = self._choice_matrix()
        self.solution_matrix = self._empty_matrix()

        self.value = value

    def _constraint_matrix(self) -> Constraints:
        constraint_numbers = [[value, i, j] for value in self.range for i in self.range for j in self.range]

        constraints: Constraints = {'some_in_column_and_row': set(),
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

    def _choice_matrix(self) -> list[ChoiceRow]:
        constraint_numbers = [[value, i, j] for i in self.range for j in self.range for value in self.range]

        result: list[ChoiceRow] = []
        for row in constraint_numbers:
            value = row[0]
            col_index = row[1]
            row_index = row[2]
            some_number_x_in_row_y = [(row_index == i and col_index == j) for i in self.range for j in self.range]
            the_number_x_in_row_y = [(value == value_ and row_index == i) for value_ in self.range for i in self.range]
            the_number_x_in_col_y = [(value == value_ and col_index == i) for value_ in self.range for i in self.range]
            result.append({'choice': value,
                           'position': [col_index, row_index],
                           'constraints': [some_number_x_in_row_y, the_number_x_in_row_y, the_number_x_in_col_y]})
        return result

    @staticmethod
    def _s(x: bool) -> str:
        if x:
            return 'X'
        return ""

    def print_choice_matrix(self) -> None:
        self._print_matrix(self.choice_matrix)

    def print_solution_matrix(self) -> None:
        self._print_matrix(self.solution_matrix)

    def _print_matrix(self, matrix: List[ChoiceRow]) -> None:
        print('{:8s} | {:10s} | {:11s} | {:11s}'.format('choice', 'some number', 'the number', 'the number'))
        print('{:8s} | {:5d} {:5d} | {:5d} {:5d} | {:4d} {:4d}'.format('', 1, 2, 1, 2, 1, 2))
        print('{:8s} | {:11s} | {:10s} | {:10s}'.format('', 'and row', 'must in row', 'must in col'))
        print(
            '{:8s} '
            '| {:2d} {:2d} {:2d} {:2d} '
            '| {:2d} {:2d} {:2d} {:2d} '
            '| {:2d} {:2d} {:2d} {:2d}'.format('',
                                               1, 2, 1, 2,
                                               1, 2, 1, 2,
                                               1, 2, 1, 2))

        for row in matrix:
            print('{:d} @ ({:d},{:d})|'.format(row['choice'], row['position'][0], row['position'][1]), end="")
            for j in row['constraints']:
                for i in j:
                    print('  {:1s}'.format(ExactCover._s(i)), end="")
                print(" |", end="")
            print()

        pass

    def rows_left_after_removing__column(self, column_number: int) -> None:
        i, j = self.constraint_column_to_xy(column_number)
        self.choice_matrix = list(filter(lambda x: not x['constraints'][i][j], self.choice_matrix))

    def constraint_column_to_xy(self, column_number: int) -> tuple[int, int]:
        i = column_number // len(self.range)
        j = column_number % len(self.range)
        return i, j

    def _empty_matrix(self) -> List[ChoiceRow]:
        return []

    def heuristic(self) -> int:
        if not self.solution_matrix:
            return 0
        total = copy.deepcopy(self.solution_matrix[0])
        total[0] = [-1, [0, 0]]
        for row_index in range(len(self.solution_matrix)):
            for column_index in range(1, len(self.solution_matrix[row_index])):
                x, y = self.constraint_column_to_xy(column_index)
                print(total)
                print(x, y)
                total[x][y] = total[x][y] or self.solution_matrix[row_index][x][y]

        for constraint in range(0, 12 + 1):
            i, j = self.constraint_column_to_xy(constraint)
            if not total[i][j]:
                return constraint
        raise ValueError("Could not find empty column")

    def select_row(self, chosen_column: int) -> ChoiceRow:
        i, j = self.constraint_column_to_xy(chosen_column)
        return list(filter(lambda x: x['constraints'][i][j], self.choice_matrix))[0]

    def add_to_solution(self, chosen_row: ChoiceRow) -> None:
        self.solution_matrix = self.solution_matrix + [chosen_row]

    def remove_from_choice(self, chosen_row: ChoiceRow) -> None:
        self.choice_matrix = list(filter(lambda row: not row == chosen_row, self.choice_matrix))


class TestIOTest(unittest.TestCase):
    def test_generate_latin_square_2x2(self) -> None:
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

    def test_generate_latin_square_2x2_2(self) -> None:
        raw_values = [
            "  ",
            "  "
        ]
        exact_cover = ExactCover(IO().load_generic(raw_values))

        choice_matrix_rows = len(exact_cover.choice_matrix) + len(exact_cover.solution_matrix)

        chosen_column = exact_cover.heuristic()
        chosen_row = exact_cover.select_row(chosen_column)
        exact_cover.add_to_solution(chosen_row)
        exact_cover.remove_from_choice(chosen_row)

        exact_cover.print_choice_matrix()

        exact_cover.print_solution_matrix()
        self.assertEqual(choice_matrix_rows, len(exact_cover.choice_matrix) + len(exact_cover.solution_matrix))


if __name__ == '__main__':
    unittest.main()
