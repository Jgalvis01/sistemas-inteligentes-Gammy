"""Escenarios de prueba para validar el comportamiento de la IA de Gammy.

Define 6 escenarios de prueba basados en los PDFs del proyecto:
1. Jaque mate en 1 movimiento
2. Defensa ante amenaza inmediata
3. Captura de pieza de mayor valor
4. Control del centro en apertura
5. Comportamiento con profundidad variable
6. Gammy vs agente aleatorio
"""

from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Dict, List, Optional

from .ai import Decision, choose_best_move, evaluate_state
from .engine import apply_move, generate_legal_moves, get_terminal_status, is_in_check
from .model import GameState, Move, Piece, board_to_text, initial_state


@dataclass
class Scenario:
    """Define un escenario de prueba con un nombre, descripción y estado inicial."""

    name: str
    description: str
    state: GameState


@dataclass
class TestResult:
    """Resultado de ejecutar una prueba sobre un escenario.

    Attributes:
        name: Nombre de la prueba.
        description: Descripción del escenario.
        passed: Si la prueba pasó o no.
        expected: Resultado esperado.
        obtained: Resultado obtenido.
        move: Movimiento elegido por la IA.
        eval_before: Evaluación heurística antes del movimiento.
        eval_after: Evaluación heurística después del movimiento.
        state_lines: Representación textual del tablero.
    """

    name: str
    description: str
    passed: bool
    expected: str
    obtained: str
    move: Optional[Move]
    eval_before: float
    eval_after: float
    state_lines: List[str]
    extra: str = ""


def parse_layout(rows: List[str], turn: str) -> GameState:
    """Construye un GameState a partir de una representación textual del tablero."""
    board: List[List[Optional[Piece]]] = [[None for _ in range(5)] for _ in range(5)]
    if len(rows) != 5:
        raise ValueError("Expected 5 rows for layout")

    for r, row in enumerate(rows):
        tokens = row.split()
        if len(tokens) != 5:
            raise ValueError("Each row must have 5 tokens")
        for c, token in enumerate(tokens):
            if token == "--":
                board[r][c] = None
                continue
            kind = token[0]
            color_code = token[1]
            kind = kind.upper()
            if color_code in ("b", "w"):
                color = "white"
            elif color_code in ("n", "k"):
                color = "black"
            else:
                raise ValueError(f"Unknown color code: {color_code}")
            board[r][c] = Piece(kind, color)

    return GameState(board=board, turn=turn)


def scenario_mate_in_one() -> Scenario:
    """Escenario donde blancas pueden dar jaque mate en un solo movimiento."""
    rows = [
        "-- -- -- -- --",
        "-- -- -- -- --",
        "-- -- Kb -- Qb",
        "-- -- -- -- Pn",
        "-- -- -- Pn Kn",
    ]
    state = parse_layout(rows, turn="white")
    return Scenario(
        name="Prueba 1",
        description="Jaque mate en 1 movimiento",
        state=state,
    )


def scenario_defense() -> Scenario:
    """Escenario donde blancas deben defenderse de una amenaza inmediata."""
    rows = [
        "-- -- -- Qb Kb",
        "-- -- -- -- --",
        "-- -- -- -- Tn",
        "-- -- -- -- --",
        "Kn -- -- -- --",
    ]
    state = parse_layout(rows, turn="white")
    return Scenario(
        name="Prueba 2",
        description="Defensa ante amenaza inmediata",
        state=state,
    )


def scenario_capture_queen() -> Scenario:
    """Escenario donde blancas pueden capturar la reina enemiga."""
    rows = [
        "Tb -- -- -- Kb",
        "-- -- -- -- --",
        "-- -- -- -- --",
        "-- -- -- -- --",
        "Qn -- -- -- Kn",
    ]
    state = parse_layout(rows, turn="white")
    return Scenario(
        name="Prueba 3",
        description="Captura de pieza de mayor valor",
        state=state,
    )


def scenario_center_opening() -> Scenario:
    """Escenario de apertura para evaluar si la IA prioriza el control del centro."""
    return Scenario(
        name="Prueba 4",
        description="Control del centro en apertura",
        state=initial_state(),
    )


def scenario_depth_variation() -> Scenario:
    """Escenario para evaluar cómo varía el comportamiento según la profundidad de búsqueda."""
    rows = [
        "Tb -- -- -- Kb",
        "-- Pb Pb -- --",
        "-- -- -- -- --",
        "-- -- Pn -- --",
        "-- -- -- -- Kn",
    ]
    state = parse_layout(rows, turn="white")
    return Scenario(
        name="Prueba 5",
        description="Comportamiento con profundidad variable",
        state=state,
    )


def scenario_vs_random() -> Scenario:
    """Escenario de partida completa: Gammy vs un agente que juega al azar."""
    return Scenario(
        name="Prueba 6",
        description="Gammy vs agente aleatorio",
        state=initial_state(),
    )


def get_scenarios() -> Dict[str, Scenario]:
    """Retorna un diccionario con todos los escenarios de prueba disponibles."""
    return {
        "mate_in_one": scenario_mate_in_one(),
        "defense": scenario_defense(),
        "capture_queen": scenario_capture_queen(),
        "center_opening": scenario_center_opening(),
        "depth_variation": scenario_depth_variation(),
        "vs_random": scenario_vs_random(),
    }


def run_test_mate_in_one(scenario: Scenario, depth: int) -> TestResult:
    """Prueba 1: Verifica que la IA encuentre jaque mate en 1 movimiento."""
    state = scenario.state
    eval_before = evaluate_state(state, "white")
    decision = choose_best_move(state, depth, "white")
    if not decision.move:
        return TestResult(
            scenario.name,
            scenario.description,
            False,
            "Mate in 1",
            "No move",
            None,
            eval_before,
            eval_before,
            board_to_text(state.board),
        )
    next_state = apply_move(state, decision.move, validate=True)
    terminal, winner, reason = get_terminal_status(next_state)
    eval_after = evaluate_state(next_state, "white")
    passed = terminal and reason == "checkmate" and winner == "white"
    obtained = f"terminal={terminal} reason={reason} winner={winner}"
    return TestResult(
        scenario.name,
        scenario.description,
        passed,
        "Mate in 1",
        obtained,
        decision.move,
        eval_before,
        eval_after,
        board_to_text(state.board),
    )


def run_test_defense(scenario: Scenario, depth: int) -> TestResult:
    """Prueba 2: Verifica que la IA se defienda correctamente ante una amenaza."""
    state = scenario.state
    eval_before = evaluate_state(state, "white")
    decision = choose_best_move(state, depth, "white")
    if not decision.move:
        return TestResult(
            scenario.name,
            scenario.description,
            False,
            "Defense move",
            "No move",
            None,
            eval_before,
            eval_before,
            board_to_text(state.board),
        )
    next_state = apply_move(state, decision.move, validate=True)
    safe = not is_in_check(next_state, "white")
    eval_after = evaluate_state(next_state, "white")
    obtained = "king safe" if safe else "king still in check"
    return TestResult(
        scenario.name,
        scenario.description,
        safe,
        "King must be safe",
        obtained,
        decision.move,
        eval_before,
        eval_after,
        board_to_text(state.board),
    )


def run_test_capture_queen(scenario: Scenario, depth: int) -> TestResult:
    """Prueba 3: Verifica que la IA capture la pieza de mayor valor disponible."""
    state = scenario.state
    eval_before = evaluate_state(state, "white")

    legal = generate_legal_moves(state, state.turn)
    capture_move = None
    for move in legal:
        if move.captured and move.captured.kind == "Q":
            capture_move = move
            break

    decision = choose_best_move(state, depth, "white")
    if not capture_move:
        return TestResult(
            scenario.name,
            scenario.description,
            False,
            "Capture available",
            "No capture move found",
            decision.move,
            eval_before,
            eval_before,
            board_to_text(state.board),
        )

    capture_state = apply_move(state, capture_move, validate=True)
    eval_after = evaluate_state(capture_state, "white")
    chosen_capture = decision.move and decision.move.as_tuple() == capture_move.as_tuple()
    obtained = "captured queen" if chosen_capture else "other move"

    return TestResult(
        scenario.name,
        scenario.description,
        chosen_capture,
        "Capture queen",
        obtained,
        decision.move,
        eval_before,
        eval_after,
        board_to_text(state.board),
    )


def run_test_center_opening(scenario: Scenario, depth: int) -> TestResult:
    """Prueba 4: Verifica que la IA mejore su control del centro en la apertura."""
    state = scenario.state
    eval_before = evaluate_state(state, "white")
    decision = choose_best_move(state, 1, "white")
    if not decision.move:
        return TestResult(
            scenario.name,
            scenario.description,
            False,
            "Center move",
            "No move",
            None,
            eval_before,
            eval_before,
            board_to_text(state.board),
        )
    next_state = apply_move(state, decision.move, validate=True)
    eval_after = evaluate_state(next_state, "white")
    from .ai import center_score

    before_center = center_score(state, "white")
    after_center = center_score(next_state, "white")
    passed = after_center > before_center
    obtained = f"center {before_center} -> {after_center}"
    return TestResult(
        scenario.name,
        scenario.description,
        passed,
        "Center control increases",
        obtained,
        decision.move,
        eval_before,
        eval_after,
        board_to_text(state.board),
    )


def run_test_depth_variation(scenario: Scenario) -> TestResult:
    """Prueba 5: Verifica que el tiempo de cómputo crece con la profundidad."""
    state = scenario.state
    results = []
    passed = True
    last_time = None

    for depth in (1, 2, 3, 4):
        start = perf_counter()
        decision = choose_best_move(state, depth, "white")
        duration = perf_counter() - start
        results.append((depth, decision.move, decision.value, duration))
        if decision.move is None:
            passed = False
        if last_time is not None and duration < last_time:
            passed = False
        last_time = duration

    summary = "; ".join(
        f"D{d}:{'none' if m is None else m.as_tuple()} val={v:.2f} t={t:.3f}s"
        for d, m, v, t in results
    )

    return TestResult(
        scenario.name,
        scenario.description,
        passed,
        "Compute time grows with depth",
        summary,
        results[-1][1],
        results[0][2],
        results[-1][2],
        board_to_text(state.board),
    )


def run_test_vs_random(scenario: Scenario, games: int = 20, depth: int = 3) -> TestResult:
    """Prueba 6: Verifica que Gammy gane consistentemente contra un agente aleatorio."""
    from random import choice


    wins = 0
    losses = 0
    draws = 0


    start = perf_counter()


    for _ in range(games):
        state = scenario.state.clone()
        ply = 0
        while True:
            terminal, winner, reason = get_terminal_status(state)
            if terminal:
                if reason == "checkmate":
                    if winner == "white":
                        wins += 1
                    else:
                        losses += 1
                else:
                    draws += 1
                break


            if ply >= 200:
                draws += 1
                break


            if state.turn == "white":
                decision = choose_best_move(state, depth, "white")
                if not decision.move:
                    draws += 1
                    break
                state = apply_move(state, decision.move, validate=True)
            else:
                moves = generate_legal_moves(state, state.turn)
                if not moves:
                    draws += 1
                    break
                state = apply_move(state, choice(moves), validate=True)


            ply += 1


    elapsed = perf_counter() - start


    win_rate = wins / games * 100
    loss_rate = losses / games * 100
    passed = win_rate >= 90 and loss_rate <= 2
    obtained = f"wins={wins} losses={losses} draws={draws} | win_rate={win_rate:.1f}% loss_rate={loss_rate:.1f}% | time={elapsed:.2f}s"
 
    return TestResult(
        scenario.name,
        f"{scenario.description} (depth={depth}, games={games})",
        passed,
        "Win rate >= 90%, losses <= 2%",
        obtained,
        None,
        0.0,
        0.0,
        board_to_text(scenario.state.board),
    )




def run_all_tests(depth: int = 3) -> List[TestResult]:
    """Ejecuta todas las pruebas y retorna la lista de resultados."""
    scenarios = get_scenarios()
    results: List[TestResult] = []


    results.append(run_test_mate_in_one(scenarios["mate_in_one"], depth))
    results.append(run_test_defense(scenarios["defense"], depth))
    results.append(run_test_capture_queen(scenarios["capture_queen"], depth))
    results.append(run_test_center_opening(scenarios["center_opening"], depth))
    results.append(run_test_depth_variation(scenarios["depth_variation"]))
    for d in (1, 2, 3):
        results.append(run_test_vs_random(scenarios["vs_random"], games=20, depth=d))
 
    return results
