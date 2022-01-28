import copy
import unittest
from functools import reduce
from operator import and_

from test_game import IO

SIZE: int = 9


class ExactCover:
    def __init__(self, value):
        # assert square matrix
        assert len(value) == len(value[0])
        # https://stackoverflow.com/questions/35429478/testing-and-assertion-in-list-comprehension
        assert reduce(and_, [len(row) == len(value[0]) for row in value])

        self.range = range(1, 2 + 1)

        self.value = value

    def _constraint_matrix(self) -> dict[str, set[str]]:
        constraint_numbers = [[value, i, j] for value in self.range for i in self.range for j in self.range]

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
        constraint_numbers = [[value, i, j] for i in self.range for j in self.range for value in self.range]

        result = []
        for row in constraint_numbers:
            value = row[0]
            col_index = row[1]
            row_index = row[2]
            some_number_x_in_row_y = [(row_index == i and col_index == j) for i in self.range for j in self.range]
            the_number_x_in_row_y = [(value == value_ and row_index == i) for value_ in self.range for i in self.range]
            the_number_x_in_col_y = [(value == value_ and col_index == i) for value_ in self.range for i in self.range]
            result.append(
                [[value, [col_index, row_index]], some_number_x_in_row_y, the_number_x_in_row_y, the_number_x_in_col_y])
        return result

    @staticmethod
    def _s(x):
        if x:
            return 'X'
        return ""

    def print_choice_matrix(self, choice_matrix):
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
            for j in range(1, len(row)):
                for i in row[j]:
                    print('  {:1s}'.format(ExactCover._s(i)), end="")
                print(" |", end="")
            print()

        pass

    def rows_left_after_removing__column(self, column_number: int, choice_matrix):
        i, j = self.constraint_column_to_xy(column_number)
        return list(filter(lambda x: not x[i][j], choice_matrix))

    def constraint_column_to_xy(self, column_number):
        non_constraint_prefix_columns = 1
        i = column_number // len(self.range) + non_constraint_prefix_columns
        j = column_number % len(self.range)
        return i, j

    def _empty_matrix(self):
        return []

    def heuristic(self, solution_matrix: list, choice_matrix: list):
        if not solution_matrix:
            return 0
        total = copy.deepcopy(solution_matrix[0])
        total[0] = [-1, [0, 0]]
        for row_index in range(len(solution_matrix)):
            for column_index in range(1, len(solution_matrix[row_index])):
                x, y = self.constraint_column_to_xy(column_index)
                print(total)
                print(x, y)
                total[x][y] = total[x][y] or solution_matrix[row_index][x][y]

        for constraint in range(0, 12 + 1):
            i, j = self.constraint_column_to_xy(constraint)
            if not total[i][j]:
                return constraint
        raise ValueError("Could not find empty column")

    def select_row(self, chosen_column: int, choice_matrix: list):
        i, j = self.constraint_column_to_xy(chosen_column)
        return list(filter(lambda x: x[i][j], choice_matrix))[0]

    def add_to_solution(self, solution_matrix: list, chosen_row: list):
        return solution_matrix + [chosen_row]

    def remove_from_choice(self, chosen_column: list, choice_matrix: list):
        return list(filter(lambda row: not row == chosen_column, choice_matrix))


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

    def test_generate_latin_square_2x2_2(self) -> None:
        raw_values = [
            "  ",
            "  "
        ]
        exact_cover = ExactCover(IO().load_generic(raw_values))
        choice_matrix = exact_cover._choice_matrix()
        choice_matrix_rows = len(choice_matrix)
        solution_matrix = exact_cover._empty_matrix()

        chosen_column = exact_cover.heuristic(solution_matrix, choice_matrix)
        chosen_row = exact_cover.select_row(chosen_column, choice_matrix)
        solution_matrix = exact_cover.add_to_solution(solution_matrix, chosen_row)
        choice_matrix = exact_cover.remove_from_choice(chosen_row, choice_matrix)

        exact_cover.print_choice_matrix(choice_matrix)

        exact_cover.print_choice_matrix(solution_matrix)
        self.assertEqual(choice_matrix_rows, len(choice_matrix) + len(solution_matrix))


if __name__ == '__main__':
    unittest.main()
