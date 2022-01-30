import copy
from functools import reduce
from operator import and_
from typing import TypedDict, Set, List, Optional

SIZE: int = 9
Constraints = TypedDict('Constraints', {'some_in_column_and_row': Set[str],
                                        'number_in_row': Set[str],
                                        'number_in_column': List[str]})
ChoiceRow = TypedDict('ChoiceRow',
                      {'choice': int,
                       'position': List[int],
                       'constraints': List[List[bool]],
                       'deleted': bool})


class ExactCover:
    choice_matrix: list[ChoiceRow]
    solution_matrix: list[ChoiceRow]

    def __init__(self, value: List[List[Optional[int]]]):
        # assert square matrix
        assert len(value) == len(value[0])
        # https://stackoverflow.com/questions/35429478/testing-and-assertion-in-list-comprehension
        assert reduce(and_, [len(row) == len(value[0]) for row in value])

        self.range = range(1, 2 + 1)
        self._number_of_constraints = range(0, 12 + 1)  # 4, 4, 4

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
                           'constraints': [some_number_x_in_row_y, the_number_x_in_row_y, the_number_x_in_col_y],
                           'deleted': False
                           })
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
        assert (len(self.range) == 2)

        print('{:8s} | {:10s} | {:11s} | {:11s}'.format('choice', 'some number', 'the number', 'the number'))
        print('{:8s} | {:5d} {:5d} | {:5d} {:5d} | {:4d} {:4d}'.format('', *self.range, *self.range, *self.range))
        print('{:8s} | {:11s} | {:10s} | {:10s}'.format('', 'and row', 'must in row', 'must in col'))
        print(
            '{:8s} '
            '| {:2d} {:2d} {:2d} {:2d} '
            '| {:2d} {:2d} {:2d} {:2d} '
            '| {:2d} {:2d} {:2d} {:2d}'.format('',
                                               *self.range, *self.range,
                                               *self.range, *self.range,
                                               *self.range, *self.range))

        for row in matrix:
            print('{:d} @ ({:d},{:d})|'.format(row['choice'], row['position'][0], row['position'][1]), end="")
            for j in row['constraints']:
                for i in j:
                    print('  {:1s}'.format(ExactCover._s(i)), end="")
                print(" |", end="")
            print()

        totals = self.compute_solution_totals()

        print('{:8s} |'.format('totals'), end="")
        for subgroup in totals:
            for cell in subgroup:
                print('  {:1d}'.format(cell), end="")
            print(" |", end="")
        print()

    def compute_solution_totals(self) -> list[list[int]]:
        totals = [[0 for i in u] for u in self.choice_matrix[0]['constraints']]
        for row in self.solution_matrix:
            for j, val in enumerate(row['constraints']):
                for k, valk in enumerate(val):
                    totals[j][k] += 1 if valk else 0

        return totals

    def rows_left_after_removing__column(self, column_number: int) -> None:
        i, j = self.constraint_column_to_xy(column_number)
        self.choice_matrix = list(filter(lambda x: not x['constraints'][i][j], self.choice_matrix))

    def constraint_column_to_xy(self, column_number: int) -> tuple[int, int]:
        i = column_number // len(self.range)
        j = column_number % len(self.range)
        return i, j

    def _empty_matrix(self) -> List[ChoiceRow]:
        return []

    def heuristic(self) -> ChoiceRow:
        if not self.solution_matrix:
            return self.choice_matrix[0]
        total = self._which_constraints_are_satisfied()

        choice_matrix = list(filter(lambda x: not x['deleted'], self.choice_matrix))

        some_column_empty = False
        for constraint in self._number_of_constraints:
            i, j = self.constraint_column_to_xy(constraint)
            some_column_empty = some_column_empty or total[i][j]

        # if not some_column_empty:
        #     raise ValueError("Could not find empty column. Complete?")

        if not choice_matrix:
            raise ValueError("Could not find any row. Complete?")

        return choice_matrix[0]

    def _which_constraints_are_satisfied(self) -> List[List[bool]]:
        total = copy.deepcopy(self.solution_matrix[0])
        total['choice'] = -1
        total['position'] = [0, 0]
        row: ChoiceRow
        for row_index, row in enumerate(self.solution_matrix):
            for column_index, _ in enumerate(row):
                x, y = self.constraint_column_to_xy(column_index)
                total['constraints'][x][y] = total['constraints'][x][y] or row['constraints'][x][y]
        return total['constraints']

    def select_row(self, chosen_column: int) -> ChoiceRow:
        i, j = self.constraint_column_to_xy(chosen_column)
        return list(filter(lambda x: x['constraints'][i][j], self.choice_matrix))[0]

    def add_to_solution(self, chosen_row: ChoiceRow) -> None:
        chosen_row_copy = copy.deepcopy(chosen_row)
        chosen_row_copy['deleted'] = False
        self.solution_matrix = self.solution_matrix + [chosen_row_copy]

    def remove_from_choice(self, chosen_row: ChoiceRow) -> None:
        for row in self.choice_matrix:
            if row == chosen_row:
                row['deleted'] = True

        for constraint_group_idx, constraint_group in enumerate(chosen_row['constraints']):
            for constraint_idx, constraint in enumerate(constraint_group):
                if constraint:
                    for choice in self.choice_matrix:
                        if choice['constraints'][constraint_group_idx][constraint_idx]:
                            choice['deleted'] = True

    def _not_deleted(self, values: List[ChoiceRow]) -> List[ChoiceRow]:
        return list(filter(lambda x: not x['deleted'], values))

    def choice_matrix_length(self) -> int:
        return len(self._not_deleted(self.choice_matrix))

    def solution_matrix_length(self) -> int:
        return len(self._not_deleted(self.solution_matrix))

    def select_row_using_heuristic(self) -> ChoiceRow:
        selected_row = self.heuristic()
        return selected_row

    def is_complete(self) -> bool:
        for group in self.compute_solution_totals():
            if min(group) == 0:
                return False
        return True
