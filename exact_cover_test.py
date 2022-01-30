import unittest
from typing import Union

from exact_cover import ChoiceRow, ExactCover
from project_io import IO


class TestExactCover(unittest.TestCase):
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

        chosen_row: Union[bool, ChoiceRow] = True
        printed = False
        while chosen_row:
            try:
                chosen_row = exact_cover.select_row_using_heuristic()
            except ValueError:
                exact_cover.print_choice_matrix()
                exact_cover.print_solution_matrix()
                printed = True
                break
            exact_cover.add_to_solution(chosen_row)
            exact_cover.remove_from_choice(chosen_row)

            self.assert_no_repeated_constraints(exact_cover)

        if not printed:
            exact_cover.print_choice_matrix()
            exact_cover.print_solution_matrix()

        self.assertTrue(exact_cover.is_complete())

    def assert_no_repeated_constraints(self, exact_cover: ExactCover) -> None:
        totals = exact_cover.compute_solution_totals()
        for total in totals:
            try:
                self.assertTrue(max(total) == 1)
            except AssertionError:
                print(totals)
                raise


if __name__ == '__main__':
    unittest.main()
