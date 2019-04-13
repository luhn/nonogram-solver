from typing import Tuple, List, Iterator, Iterable
from enum import Enum


Hints = List[int]
Guesses = List[int]


class Pixel(Enum):
    UNKNOWN = 0
    FILLED = 1
    EMPTY = -1


class Board:
    size: int
    board: List[List[Pixel]]
    row_guesses: List[List[Guesses]]
    col_guesses: List[List[Guesses]]
    row_hints: List[Hints]
    col_hints: List[Hints]

    def __init__(self, size: int, row_hints: List[Hints], col_hints: List[Hints]):
        assert len(row_hints) == size
        assert len(col_hints) == size
        self.size = size
        self.row_hints = row_hints
        self.col_hints = col_hints
        self.clear_board()
        self.enumerate_possibilities()

    def clear_board(self) -> None:
        self.board = []
        for _ in range(self.size):
            self.board.append([Pixel.UNKNOWN for _ in range(self.size)])

    def enumerate_possibilities(self) -> None:
        self.row_guesses = []
        for row, hints in zip(self.rows, self.row_hints):
            self.row_guesses.append(list(possibilities(self.size, hints)))
        self.col_guesses = []
        for col, hints in zip(self.cols, self.col_hints):
            self.col_guesses.append(list(possibilities(self.size, hints)))

    def run_row_pass(self) -> None:
        for index, row in enumerate(self.rows):
            guesses = self.row_guesses[index]
            hints = self.row_hints[index]
            self.row_guesses[index] = list(filter_possibilities(row, hints, guesses))
        for index, guesses in enumerate(self.row_guesses):
            distilled = distill_possibilities(self.size, self.row_hints[index], guesses)
            self.set_row(index, distilled)

    def run_col_pass(self) -> None:
        for index, col in enumerate(self.cols):
            guesses = self.col_guesses[index]
            hints = self.col_hints[index]
            self.col_guesses[index] = list(filter_possibilities(col, hints, guesses))
        for index, guesses in enumerate(self.col_guesses):
            distilled = distill_possibilities(self.size, self.col_hints[index], guesses)
            self.set_col(index, distilled)

    def is_solved(self) -> bool:
        for row in self.rows:
            if any(pixel == Pixel.UNKNOWN for pixel in row):
                return False
        return True

    @property
    def rows(self) -> Iterator[List[Pixel]]:
        return iter(self.board)

    def set_row(self, index: int, row: List[Pixel]) -> None:
        assert len(row) == self.size
        self.board[index] = row

    @property
    def cols(self) -> Iterator[List[Pixel]]:
        for i in range(self.size):
            yield [row[i] for row in self.board]

    def set_col(self, index: int, row: List[Pixel]) -> None:
        assert len(row) == self.size
        for j, item in enumerate(row):
            self.board[j][index] = item

    def solve(self) -> None:
        for i in range(100):
            self.run_row_pass()
            self.run_col_pass()
            if self.is_solved():
                break
        else:
            raise ValueError("Could not solve in 100 iterations.")

    def print(self) -> None:
        MAP = {Pixel.UNKNOWN: " ", Pixel.FILLED: "#", Pixel.EMPTY: "X"}
        for row in self.rows:
            print(" ".join(MAP[pixel] for pixel in row))


def possibilities(size: int, hints: Hints) -> Iterator[Guesses]:
    if len(hints) == 0:
        return
    length = hints[0]
    upcoming = hints[1:]
    if len(upcoming) == 0:
        assert size >= length
        for position in range(size - length + 1):
            yield [position]
    else:
        upcomingSize = sum(upcoming) + len(upcoming) - 1
        for position in range(size - length - upcomingSize):
            offset = position + length + 1
            for possibility in possibilities(size - offset, upcoming):
                yield [position] + [x + offset for x in possibility]


def walk_possibility(size: int, hints: Hints, guesses: Guesses) -> Iterator[Pixel]:
    offset = 0
    for position, length in zip(guesses, hints):
        for _ in range(position - offset):
            yield Pixel.EMPTY
        for _ in range(length):
            yield Pixel.FILLED
        offset = position + length
    for _ in range(size - offset):
        yield Pixel.EMPTY


def filter_possibilities(
    row: List[Pixel], hints: Hints, guesses: Iterable[Guesses]
) -> Iterator[Guesses]:
    size = len(row)
    for guess in guesses:
        walker = walk_possibility(size, hints, guess)
        for pixel, check in zip(row, walker):
            if pixel is not Pixel.UNKNOWN and pixel is not check:
                break
        else:
            yield guess


def distill_possibilities(
    size: int, hints: Hints, guesses: Iterable[Guesses]
) -> List[Pixel]:
    guesses = iter(guesses)
    if len(hints) == 0:
        return [Pixel.EMPTY for _ in range(size)]
    distilled = list(walk_possibility(size, hints, next(guesses)))
    for guess in guesses:
        new_distilled = []
        walker = walk_possibility(size, hints, guess)
        for pixel, check in zip(distilled, walker):
            if pixel is not Pixel.UNKNOWN and pixel is check:
                new_distilled.append(check)
            else:
                new_distilled.append(Pixel.UNKNOWN)
        distilled = new_distilled
    return distilled


if __name__ == "__main__":
    pass
