"""Inteligencia artificial para Gammy (Gardner Minichess 5x5).

Implementa la función de evaluación heurística del tablero y el algoritmo
Minimax con poda alfa-beta para seleccionar el mejor movimiento.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional, Tuple

from .constants import CENTER_SQUARES, PIECE_VALUES, WEIGHTS
from .engine import generate_legal_moves, get_terminal_status, opponent
from .model import GameState, Move, Piece


@dataclass
class Decision:
    """Resultado de la búsqueda del mejor movimiento.

    Attributes:
        move: Mejor movimiento encontrado (None si no hay movimientos legales).
        value: Valor heurístico del movimiento.
        nodes: Cantidad de nodos explorados en la búsqueda.
    """

    move: Optional[Move]
    value: float
    nodes: int


def evaluate_state(state: GameState, perspective: str) -> float:
    """Evalúa el estado del tablero desde la perspectiva del color dado.

    Combina cuatro heurísticas ponderadas: material, control del centro,
    seguridad del rey y movilidad.
    """
    terminal, winner, reason = get_terminal_status(state)
    if terminal:
        if reason == "checkmate":
            return float("inf") if winner == perspective else float("-inf")
        return 0.0

    material = material_score(state, perspective)
    center = center_score(state, perspective)
    king_safety = king_safety_score(state, perspective)
    mobility = mobility_score(state, perspective)

    return (
        WEIGHTS["material"] * material
        + WEIGHTS["center"] * center
        + WEIGHTS["king_safety"] * king_safety
        + WEIGHTS["mobility"] * mobility
    )


def material_score(state: GameState, perspective: str) -> float:
    """Calcula la diferencia de material (valor de piezas propias - oponente)."""
    own = 0
    opp = 0
    for row in state.board:
        for piece in row:
            if not piece:
                continue
            value = PIECE_VALUES[piece.kind]
            if piece.color == perspective:
                own += value
            else:
                opp += value
    return float(own - opp)


def center_score(state: GameState, perspective: str) -> float:
    """Calcula la diferencia de piezas en casillas centrales del tablero."""
    own = 0
    opp = 0
    for (row, col) in CENTER_SQUARES:
        piece = state.board[row][col]
        if not piece:
            continue
        if piece.color == perspective:
            own += 1
        else:
            opp += 1
    return float(own - opp)


def king_safety_score(state: GameState, perspective: str) -> float:
    """Calcula la diferencia de seguridad del rey (piezas aliadas adyacentes)."""
    own = adjacent_friends(state, perspective)
    opp = adjacent_friends(state, opponent(perspective))
    return float(own - opp)


def adjacent_friends(state: GameState, color: str) -> int:
    """Cuenta cuántas piezas aliadas rodean al rey del color dado."""
    from .constants import BOARD_SIZE, KING_OFFSETS
    from .engine import find_king

    king_pos = find_king(state, color)
    if not king_pos:
        return 0
    count = 0
    row, col = king_pos
    for dr, dc in KING_OFFSETS:
        r, c = row + dr, col + dc
        if 0 <= r < BOARD_SIZE and 0 <= c < BOARD_SIZE:
            piece = state.board[r][c]
            if piece and piece.color == color:
                count += 1
    return count


def mobility_score(state: GameState, perspective: str) -> float:
    """Calcula la diferencia de movilidad (movimientos legales propios - oponente)."""
    own = len(generate_legal_moves(state, perspective))
    opp = len(generate_legal_moves(state, opponent(perspective)))
    return float(own - opp)


def choose_best_move(state: GameState, depth: int, perspective: str) -> Decision:
    """Selecciona el mejor movimiento usando Minimax con poda alfa-beta.

    Evalúa todos los movimientos legales a la profundidad indicada y
    retorna el movimiento con mejor evaluación heurística.
    """
    moves = generate_legal_moves(state, state.turn)
    if not moves:
        return Decision(None, evaluate_state(state, perspective), 1)

    best_move = None
    best_value = float("-inf") if state.turn == perspective else float("inf")
    nodes = 0

    for move in moves:
        child = apply_move_no_validation(state, move)
        value, visited = minimax(child, depth - 1, float("-inf"), float("inf"), perspective)
        nodes += visited
        if state.turn == perspective:
            if value > best_value:
                best_value = value
                best_move = move
        else:
            if value < best_value:
                best_value = value
                best_move = move

    return Decision(best_move, best_value, nodes)


def minimax(
    state: GameState,
    depth: int,
    alpha: float,
    beta: float,
    perspective: str,
) -> Tuple[float, int]:
    """Algoritmo Minimax con poda alfa-beta.

    Explora el árbol de juego recursivamente, maximizando para el jugador
    de perspectiva y minimizando para el oponente. La poda alfa-beta
    descarta ramas que no pueden mejorar el resultado.
    """
    terminal, _, _ = get_terminal_status(state)
    if depth == 0 or terminal:
        return evaluate_state(state, perspective), 1

    moves = generate_legal_moves(state, state.turn)
    if not moves:
        return evaluate_state(state, perspective), 1

    nodes = 0
    if state.turn == perspective:
        value = float("-inf")
        for move in moves:
            child = apply_move_no_validation(state, move)
            score, visited = minimax(child, depth - 1, alpha, beta, perspective)
            nodes += visited
            value = max(value, score)
            alpha = max(alpha, value)
            if beta <= alpha:
                break
        return value, nodes

    value = float("inf")
    for move in moves:
        child = apply_move_no_validation(state, move)
        score, visited = minimax(child, depth - 1, alpha, beta, perspective)
        nodes += visited
        value = min(value, score)
        beta = min(beta, value)
        if beta <= alpha:
            break
    return value, nodes


def apply_move_no_validation(state: GameState, move: Move) -> GameState:
    """Aplica un movimiento sin validar legalidad (usado internamente por Minimax)."""
    from .engine import apply_move

    return apply_move(state, move, validate=False)
