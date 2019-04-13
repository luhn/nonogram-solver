import pytest
from nonogram_solver import (
    Pixel,
    Board,
    possibilities,
    walk_possibility,
    filter_possibilities,
    distill_possibilities,
)


class TestBoard:
    def make_board(self):
        """
        # # #
        X # #
        # X X
        """
        return Board(3, [[3], [2], [1]], [[1, 1], [2], [2]])

    def test_clear_board(self):
        board = self.make_board()
        board.board = None
        board.clear_board()
        assert board.board == [
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
        ]

    def test_enumerate_possibilities(self):
        board = self.make_board()
        assert board.row_guesses == [[[0]], [[0], [1]], [[0], [1], [2]]]
        assert board.col_guesses == [[[0, 2]], [[0], [1]], [[0], [1]]]

    def test_is_solved(self):
        board = self.make_board()
        board.board = [
            [Pixel.FILLED, Pixel.FILLED, Pixel.FILLED],
            [Pixel.EMPTY, Pixel.FILLED, Pixel.FILLED],
            [Pixel.FILLED, Pixel.EMPTY, Pixel.EMPTY],
        ]
        assert board.is_solved()
        board.board[1][1] = Pixel.UNKNOWN
        assert not board.is_solved()

    def test_get_rows(self):
        board = self.make_board()
        board.board[1][2] = Pixel.FILLED
        board.board[2][2] = Pixel.EMPTY
        assert list(board.rows) == [
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.FILLED],
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.EMPTY],
        ]

    def test_set_row(self):
        board = self.make_board()
        board.set_row(1, [Pixel.UNKNOWN, Pixel.FILLED, Pixel.EMPTY])
        assert board.board == [
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.FILLED, Pixel.EMPTY],
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
        ]

    def test_get_cols(self):
        board = self.make_board()
        board.board[1][2] = Pixel.FILLED
        board.board[2][2] = Pixel.EMPTY
        assert list(board.cols) == [
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.FILLED, Pixel.EMPTY],
        ]

    def test_set_col(self):
        board = self.make_board()
        board.set_col(1, [Pixel.UNKNOWN, Pixel.FILLED, Pixel.EMPTY])
        assert board.board == [
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.FILLED, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.EMPTY, Pixel.UNKNOWN],
        ]

    def test_run_row_pass(self):
        board = self.make_board()
        board.run_row_pass()
        assert board.board == [
            [Pixel.FILLED, Pixel.FILLED, Pixel.FILLED],
            [Pixel.UNKNOWN, Pixel.FILLED, Pixel.UNKNOWN],
            [Pixel.UNKNOWN, Pixel.UNKNOWN, Pixel.UNKNOWN],
        ]

    def test_run_col_pass(self):
        board = self.make_board()
        board.run_col_pass()
        assert board.board == [
            [Pixel.FILLED, Pixel.UNKNOWN, Pixel.UNKNOWN],
            [Pixel.EMPTY, Pixel.FILLED, Pixel.FILLED],
            [Pixel.FILLED, Pixel.UNKNOWN, Pixel.UNKNOWN],
        ]

    def test_solve(self):
        board = self.make_board()
        board.solve()
        assert board.board == [
            [Pixel.FILLED, Pixel.FILLED, Pixel.FILLED],
            [Pixel.EMPTY, Pixel.FILLED, Pixel.FILLED],
            [Pixel.FILLED, Pixel.EMPTY, Pixel.EMPTY],
        ]
        assert False


class TestPossibilities:
    def test_possibilities_single(self):
        assert list(possibilities(3, [])) == []
        assert list(possibilities(1, [1])) == [[0]]
        assert list(possibilities(3, [1])) == [[0], [1], [2]]
        assert list(possibilities(4, [2])) == [[0], [1], [2]]
        assert list(possibilities(5, [2])) == [[0], [1], [2], [3]]

    def test_possibilities_double(self):
        assert list(possibilities(3, [1, 1])) == [[0, 2]]
        assert list(possibilities(4, [1, 1])) == [[0, 2], [0, 3], [1, 3]]
        assert list(possibilities(5, [1, 1])) == [
            [0, 2],
            [0, 3],
            [0, 4],
            [1, 3],
            [1, 4],
            [2, 4],
        ]
        assert list(possibilities(5, [2, 1])) == [[0, 3], [0, 4], [1, 4]]

    def test_possibilities_triple(self):
        assert list(possibilities(5, [1, 1, 1])) == [[0, 2, 4]]
        assert list(possibilities(6, [1, 1, 1])) == [
            [0, 2, 4],
            [0, 2, 5],
            [0, 3, 5],
            [1, 3, 5],
        ]
        assert list(possibilities(7, [1, 1, 1])) == [
            [0, 2, 4],
            [0, 2, 5],
            [0, 2, 6],
            [0, 3, 5],
            [0, 3, 6],
            [0, 4, 6],
            [1, 3, 5],
            [1, 3, 6],
            [1, 4, 6],
            [2, 4, 6],
        ]

    def test_possibilities_error(self):
        with pytest.raises(AssertionError):
            list(possibilities(1, [2]))


def test_walk_possibility():
    assert list(walk_possibility(2, [], [])) == [Pixel.EMPTY, Pixel.EMPTY]
    assert list(walk_possibility(2, [1], [0])) == [Pixel.FILLED, Pixel.EMPTY]
    assert list(walk_possibility(5, [1, 1, 1], [0, 2, 4])) == [
        Pixel.FILLED,
        Pixel.EMPTY,
        Pixel.FILLED,
        Pixel.EMPTY,
        Pixel.FILLED,
    ]
    assert list(walk_possibility(6, [1, 2], [1, 3])) == [
        Pixel.EMPTY,
        Pixel.FILLED,
        Pixel.EMPTY,
        Pixel.FILLED,
        Pixel.FILLED,
        Pixel.EMPTY,
    ]


class TestFilterPossibilities:
    def test_filter_possibilities_single(self):
        row = [Pixel.UNKNOWN, Pixel.FILLED, Pixel.EMPTY]
        guesses = [[0], [1], [2]]
        assert list(filter_possibilities(row, [1], guesses)) == [[1]]
        assert list(filter_possibilities(row, [2], guesses)) == [[0]]

    def test_filter_possibilities_double(self):
        row = [
            Pixel.UNKNOWN,
            Pixel.UNKNOWN,
            Pixel.UNKNOWN,
            Pixel.FILLED,
            Pixel.EMPTY,
            Pixel.UNKNOWN,
        ]
        hints = [2, 1]
        good = [[0, 3], [2, 5]]
        bad = [[0, 4], [0, 5], [1, 4], [1, 5]]
        assert list(filter_possibilities(row, hints, good + bad)) == good


class TestDistillPossibilities:
    def test_distill_possibilites_none(self):
        assert distill_possibilities(2, [], []) == [Pixel.EMPTY, Pixel.EMPTY]

    def test_distill_possibilites_single(self):
        assert distill_possibilities(4, [2], iter([[0], [1]])) == [
            Pixel.UNKNOWN,
            Pixel.FILLED,
            Pixel.UNKNOWN,
            Pixel.EMPTY,
        ]

    def test_distill_possibilities_double(self):
        assert distill_possibilities(5, [1, 1], iter([[0, 2], [2, 4]])) == [
            Pixel.UNKNOWN,
            Pixel.EMPTY,
            Pixel.FILLED,
            Pixel.EMPTY,
            Pixel.UNKNOWN,
        ]
