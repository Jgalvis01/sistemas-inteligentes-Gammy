from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .constants import BOARD_SIZE, FILES, RANKS


@dataclass(frozen=True)
class Piece:
    kind: str
    color: str

    def short_name(self) -> str:
        return f"{self.kind}{'b' if self.color == 'white' else 'n'}"


@dataclass(frozen=True)
class Move:
    from_row: int
    from_col: int
    to_row: int
    to_col: int
    piece: Piece
    captured: Optional[Piece] = None
    promotion: Optional[str] = None

    def as_tuple(self) -> Tuple[int, int, int, int, Optional[str]]:
        return (self.from_row, self.from_col, self.to_row, self.to_col, self.promotion)


@dataclass
class GameState:
    board: List[List[Optional[Piece]]]
    turn: str
    move_history: List[Move] = field(default_factory=list)
    state_history: List[str] = field(default_factory=list)
    halfmove_clock: int = 0
    castle_rights: dict = field(default_factory=lambda: {"white": False, "black": False})
    en_passant_target: Optional[Tuple[int, int]] = None

    def clone(self) -> "GameState":
        return GameState(
            board=copy_board(self.board),
            turn=self.turn,
            move_history=list(self.move_history),
            state_history=list(self.state_history),
            halfmove_clock=self.halfmove_clock,
            castle_rights=dict(self.castle_rights),
            en_passant_target=self.en_passant_target,
        )


def copy_board(board: List[List[Optional[Piece]]]) -> List[List[Optional[Piece]]]:
    return [[cell for cell in row] for row in board]


def initial_state() -> GameState:
    board = [[None for _ in range(BOARD_SIZE)] for _ in range(BOARD_SIZE)]

    # White pieces
    board[0] = [
        Piece("T", "white"),
        Piece("C", "white"),
        Piece("A", "white"),
        Piece("Q", "white"),
        Piece("K", "white"),
    ]
    for col in range(BOARD_SIZE):
        board[1][col] = Piece("P", "white")

    # Black pieces
    board[4] = [
        Piece("T", "black"),
        Piece("C", "black"),
        Piece("A", "black"),
        Piece("Q", "black"),
        Piece("K", "black"),
    ]
    for col in range(BOARD_SIZE):
        board[3][col] = Piece("P", "black")

    return GameState(board=board, turn="white")


def in_bounds(row: int, col: int) -> bool:
    return 0 <= row < BOARD_SIZE and 0 <= col < BOARD_SIZE


def state_signature(state: GameState) -> str:
    parts = [state.turn]
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = state.board[row][col]
            parts.append(piece.short_name() if piece else "--")
    parts.append("c" if state.castle_rights.get("white") else "-")
    parts.append("C" if state.castle_rights.get("black") else "-")
    parts.append(str(state.en_passant_target) if state.en_passant_target else "-")
    return "|".join(parts)


def coords_to_algebraic(row: int, col: int) -> str:
    return f"{FILES[col]}{RANKS[row]}"


def move_to_notation(move: Move) -> str:
    src = coords_to_algebraic(move.from_row, move.from_col)
    dst = coords_to_algebraic(move.to_row, move.to_col)
    capture = "x" if move.captured else "-"
    promotion = f"={move.promotion}" if move.promotion else ""
    return f"{move.piece.kind}{capture}{src}{dst}{promotion}"


def board_to_text(board: List[List[Optional[Piece]]]) -> List[str]:
    rows = []
    for row in range(BOARD_SIZE - 1, -1, -1):
        parts = []
        for col in range(BOARD_SIZE):
            piece = board[row][col]
            parts.append(piece.short_name() if piece else "--")
        rows.append(" ".join(parts))
    return rows
