import functools
from functools import reduce
from operator import and_
from typing import List, Optional, Callable, Any, TypedDict

from logzero import logger  # type: ignore

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

        return selected_positions

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