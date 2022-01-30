from typing import List, Optional

from sudoku import Sudoku


class IO:
    def load(self, raw_values: List[str]) -> Sudoku:
        return Sudoku(self.load_generic(raw_values))

    def load_generic(self, raw_values: List[str]) -> List[List[Optional[int]]]:
        return [list(map(lambda x: int(x) if x != ' ' and x != '.' else None, raw_value)) for raw_value in
                raw_values]

    def serialize(self, sudoku: Sudoku) -> List[str]:
        return ["".join(map(lambda x: x.__str__() if x is not None else ' ', raw_value)) for raw_value in
                sudoku.value]
