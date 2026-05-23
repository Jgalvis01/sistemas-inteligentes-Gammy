from __future__ import annotations

from typing import List, Optional, Tuple

from .constants import (
    BOARD_SIZE,
    DIR_DIAG,
    DIR_ORTHO,
    KING_OFFSETS,
    KNIGHT_OFFSETS,
    PROMOTION_CHOICES,
)
from .model import GameState, Move, Piece, copy_board, in_bounds, state_signature


def opponent(color: str) -> str:
    return "black" if color == "white" else "white"


def find_king(state: GameState, color: str) -> Optional[Tuple[int, int]]:
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = state.board[row][col]
            if piece and piece.color == color and piece.kind == "K":
                return row, col
    return None


def is_square_attacked(state: GameState, row: int, col: int, by_color: str) -> bool:
    board = state.board

    # Pawn attacks
    pawn_dir = 1 if by_color == "white" else -1
    for dc in (-1, 1):
        r = row - pawn_dir
        c = col - dc
        if in_bounds(r, c):
            piece = board[r][c]
            if piece and piece.color == by_color and piece.kind == "P":
                return True

    # Knight attacks
    for dr, dc in KNIGHT_OFFSETS:
        r, c = row + dr, col + dc
        if in_bounds(r, c):
            piece = board[r][c]
            if piece and piece.color == by_color and piece.kind == "C":
                return True

    # King attacks
    for dr, dc in KING_OFFSETS:
        r, c = row + dr, col + dc
        if in_bounds(r, c):
            piece = board[r][c]
            if piece and piece.color == by_color and piece.kind == "K":
                return True

    # Sliding pieces
    for dr, dc in DIR_ORTHO:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            piece = board[r][c]
            if piece:
                if piece.color == by_color and piece.kind in ("T", "Q"):
                    return True
                break
            r += dr
            c += dc

    for dr, dc in DIR_DIAG:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            piece = board[r][c]
            if piece:
                if piece.color == by_color and piece.kind in ("A", "Q"):
                    return True
                break
            r += dr
            c += dc

    return False


def is_in_check(state: GameState, color: str) -> bool:
    king_pos = find_king(state, color)
    if not king_pos:
        return False
    return is_square_attacked(state, king_pos[0], king_pos[1], opponent(color))


def generate_legal_moves(state: GameState, color: Optional[str] = None) -> List[Move]:
    color = color or state.turn
    moves: List[Move] = []
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            piece = state.board[row][col]
            if not piece or piece.color != color:
                continue
            for move in generate_piece_moves(state, row, col):
                next_state = apply_move(state, move, validate=False)
                if not is_in_check(next_state, color):
                    moves.append(move)
    return moves


def generate_piece_moves(state: GameState, row: int, col: int) -> List[Move]:
    piece = state.board[row][col]
    if not piece:
        return []

    if piece.kind == "P":
        return pawn_moves(state, row, col, piece)
    if piece.kind == "C":
        return knight_moves(state, row, col, piece)
    if piece.kind == "A":
        return bishop_moves(state, row, col, piece)
    if piece.kind == "T":
        return rook_moves(state, row, col, piece)
    if piece.kind == "Q":
        return queen_moves(state, row, col, piece)
    if piece.kind == "K":
        return king_moves(state, row, col, piece)

    return []


def pawn_moves(state: GameState, row: int, col: int, piece: Piece) -> List[Move]:
    moves: List[Move] = []
    direction = 1 if piece.color == "white" else -1
    start_row = 1 if piece.color == "white" else 3
    promotion_row = 4 if piece.color == "white" else 0
    board = state.board

    def add_pawn_move(to_row: int, to_col: int, captured: Optional[Piece]) -> None:
        if to_row == promotion_row:
            for promotion in PROMOTION_CHOICES:
                moves.append(
                    Move(row, col, to_row, to_col, piece, captured, promotion)
                )
        else:
            moves.append(Move(row, col, to_row, to_col, piece, captured))

    one_step = row + direction
    if in_bounds(one_step, col) and board[one_step][col] is None:
        add_pawn_move(one_step, col, None)
        two_step = row + (2 * direction)
        if row == start_row and in_bounds(two_step, col) and board[two_step][col] is None:
            moves.append(Move(row, col, two_step, col, piece, None))

    for dc in (-1, 1):
        r = row + direction
        c = col + dc
        if in_bounds(r, c):
            target = board[r][c]
            if target and target.color != piece.color and target.kind != "K":
                add_pawn_move(r, c, target)
    return moves


def knight_moves(state: GameState, row: int, col: int, piece: Piece) -> List[Move]:
    moves: List[Move] = []
    board = state.board
    for dr, dc in KNIGHT_OFFSETS:
        r, c = row + dr, col + dc
        if not in_bounds(r, c):
            continue
        target = board[r][c]
        if not target:
            moves.append(Move(row, col, r, c, piece, None))
        elif target.color != piece.color and target.kind != "K":
            moves.append(Move(row, col, r, c, piece, target))
    return moves


def bishop_moves(state: GameState, row: int, col: int, piece: Piece) -> List[Move]:
    return sliding_moves(state, row, col, piece, DIR_DIAG)


def rook_moves(state: GameState, row: int, col: int, piece: Piece) -> List[Move]:
    return sliding_moves(state, row, col, piece, DIR_ORTHO)


def queen_moves(state: GameState, row: int, col: int, piece: Piece) -> List[Move]:
    return sliding_moves(state, row, col, piece, DIR_ORTHO + DIR_DIAG)


def king_moves(state: GameState, row: int, col: int, piece: Piece) -> List[Move]:
    moves: List[Move] = []
    board = state.board
    for dr, dc in KING_OFFSETS:
        r, c = row + dr, col + dc
        if not in_bounds(r, c):
            continue
        target = board[r][c]
        if not target:
            moves.append(Move(row, col, r, c, piece, None))
        elif target.color != piece.color and target.kind != "K":
            moves.append(Move(row, col, r, c, piece, target))
    return moves


def sliding_moves(
    state: GameState,
    row: int,
    col: int,
    piece: Piece,
    directions: List[Tuple[int, int]],
) -> List[Move]:
    moves: List[Move] = []
    board = state.board
    for dr, dc in directions:
        r, c = row + dr, col + dc
        while in_bounds(r, c):
            target = board[r][c]
            if target is None:
                moves.append(Move(row, col, r, c, piece, None))
            else:
                if target.color != piece.color and target.kind != "K":
                    moves.append(Move(row, col, r, c, piece, target))
                break
            r += dr
            c += dc
    return moves


def apply_move(state: GameState, move: Move, validate: bool = True) -> GameState:
    if validate:
        legal = generate_legal_moves(state, state.turn)
        if not any(m.as_tuple() == move.as_tuple() for m in legal):
            raise ValueError("Illegal move")

    board = copy_board(state.board)
    captured = board[move.to_row][move.to_col]
    board[move.from_row][move.from_col] = None
    placed_piece = move.piece
    if move.promotion:
        placed_piece = Piece(move.promotion, move.piece.color)
    board[move.to_row][move.to_col] = placed_piece

    next_state = GameState(
        board=board,
        turn=opponent(state.turn),
        move_history=list(state.move_history) + [move],
        state_history=list(state.state_history) + [state_signature(state)],
        halfmove_clock=(0 if captured else state.halfmove_clock + 1),
        castle_rights=dict(state.castle_rights),
        en_passant_target=None,
    )
    return next_state


def is_threefold_repetition(state: GameState) -> bool:
    signature = state_signature(state)
    occurrences = sum(1 for past in state.state_history if past == signature)
    return occurrences >= 2


def get_terminal_status(state: GameState) -> Tuple[bool, Optional[str], str]:
    if state.halfmove_clock >= 50:
        return True, None, "50-move rule"
    if is_threefold_repetition(state):
        return True, None, "threefold repetition"

    moves = generate_legal_moves(state, state.turn)
    if moves:
        return False, None, ""

    if is_in_check(state, state.turn):
        return True, opponent(state.turn), "checkmate"
    return True, None, "stalemate"
