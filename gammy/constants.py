BOARD_SIZE = 5

COLORS = ("white", "black")
PIECE_TYPES = ("P", "C", "A", "T", "Q", "K")

PIECE_VALUES = {
    "P": 1,
    "C": 3,
    "A": 3,
    "T": 5,
    "Q": 9,
    "K": 1000,
}

PROMOTION_CHOICES = ("Q", "T", "A", "C")

WEIGHTS = {
    "material": 0.40,
    "center": 0.25,
    "king_safety": 0.20,
    "mobility": 0.15,
}

CENTER_SQUARES = {
    (1, 1), (1, 2), (1, 3),
    (2, 1), (2, 2), (2, 3),
    (3, 1), (3, 2), (3, 3),
}

KING_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
]

KNIGHT_OFFSETS = [
    (-2, -1), (-2, 1),
    (-1, -2), (-1, 2),
    (1, -2), (1, 2),
    (2, -1), (2, 1),
]

DIR_ORTHO = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIR_DIAG = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

FILES = ["a", "b", "c", "d", "e"]
RANKS = ["1", "2", "3", "4", "5"]
