"""Interfaz gráfica de Gammy (Gardner Minichess 5x5).

Implementa la ventana principal con el tablero visual, panel de controles,
historial de movimientos y log de decisiones de la IA. Usa PySide6 (Qt)
para la renderización y muestra imágenes PNG de las piezas en el tablero.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QMainWindow,
    QPushButton,
    QSlider,
    QSpinBox,
    QVBoxLayout,
    QWidget,
    QPlainTextEdit,
)

from .ai import choose_best_move, evaluate_state
from .engine import apply_move, generate_legal_moves, get_terminal_status, is_in_check
from .model import GameState, Move, Piece, initial_state, move_to_notation
from .tests import get_scenarios, run_all_tests

# Path to the images directory (sibling of the gammy package folder)
_IMAGES_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "images")

# Mapping from piece kind to the base image filename
_KIND_TO_FILE: Dict[str, str] = {
    "T": "tower",
    "C": "horse",
    "A": "bishop",
    "Q": "queen",
    "K": "king",
    "P": "paw",
}


@dataclass
class LoggedDecision:
    """Registro de una decisión tomada por la IA durante la partida."""

    move: Move
    value: float
    nodes: int


class BoardWidget(QWidget):
    """Widget que representa el tablero 5x5 con imágenes de piezas.

    Muestra las piezas como imágenes PNG cargadas desde la carpeta 'images/'.
    Soporta resaltado de casillas para el último movimiento y jaque.
    """
    # Size for each piece image (fits inside the 70x70 cell with some padding)
    _ICON_SIZE = 58

    def __init__(self) -> None:
        super().__init__()
        self.grid = QGridLayout(self)
        self.grid.setSpacing(0)
        self.labels: List[List[QLabel]] = []
        self._pixmap_cache: Dict[str, QPixmap] = {}
        self._init_grid()

    def _load_pixmap(self, piece: Piece) -> QPixmap:
        """Load and cache a scaled QPixmap for the given piece."""
        cache_key = f"{piece.color}_{piece.kind}"
        if cache_key not in self._pixmap_cache:
            base_name = _KIND_TO_FILE.get(piece.kind, piece.kind.lower())
            if piece.color == "black":
                filename = f"Black_{base_name}.png"
            else:
                filename = f"{base_name}.png"
            path = os.path.join(_IMAGES_DIR, filename)
            pixmap = QPixmap(path)
            if not pixmap.isNull():
                pixmap = pixmap.scaled(
                    self._ICON_SIZE, self._ICON_SIZE,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            self._pixmap_cache[cache_key] = pixmap
        return self._pixmap_cache[cache_key]

    def _init_grid(self) -> None:
        """Crea la cuadrícula de 5x5 QLabels con colores de casilla alternados."""
        for row in range(5):
            row_labels: List[QLabel] = []
            for col in range(5):
                label = QLabel("", self)
                label.setAlignment(Qt.AlignCenter)
                label.setFixedSize(70, 70)
                label.setProperty("coord", (row, col))
                self.grid.addWidget(label, 4 - row, col)
                row_labels.append(label)
            self.labels.append(row_labels)
        self.setStyleSheet(
            "QLabel { background: #f4f1ea; border: 1px solid #d1c7b7; color: #111111; }"
            "QLabel[dark='true'] { background: #c9b79c; }"
            "QLabel[highlight='from'] { background: #ffe08a; }"
            "QLabel[highlight='to'] { background: #a6e3a1; }"
            "QLabel[highlight='check'] { background: #f28c8c; }"
        )
        self._apply_square_colors()

    def _apply_square_colors(self) -> None:
        """Restaura los colores originales de las casillas (claro/oscuro)."""
        for row in range(5):
            for col in range(5):
                label = self.labels[row][col]
                if (row + col) % 2 == 1:
                    label.setProperty("dark", "true")
                else:
                    label.setProperty("dark", "false")
                label.setProperty("highlight", "")
        self._refresh_styles()

    def _refresh_styles(self) -> None:
        """Fuerza la actualización visual de los estilos Qt en todas las casillas."""
        for row in range(5):
            for col in range(5):
                label = self.labels[row][col]
                label.style().unpolish(label)
                label.style().polish(label)

    def set_state(self, state: GameState) -> None:
        """Actualiza el tablero visual con el estado actual de la partida."""
        for row in range(5):
            for col in range(5):
                piece = state.board[row][col]
                label = self.labels[row][col]
                if piece:
                    pixmap = self._load_pixmap(piece)
                    label.setPixmap(pixmap)
                    label.setText("")
                else:
                    label.setPixmap(QPixmap())  # clear pixmap
                    label.setText("")
        self._apply_square_colors()

    def highlight_move(self, move: Optional[Move], check_square: Optional[Tuple[int, int]]) -> None:
        """Resalta las casillas del último movimiento y la casilla de jaque."""
        self._apply_square_colors()
        if move:
            self.labels[move.from_row][move.from_col].setProperty("highlight", "from")
            self.labels[move.to_row][move.to_col].setProperty("highlight", "to")
        if check_square:
            row, col = check_square
            self.labels[row][col].setProperty("highlight", "check")
        self._refresh_styles()

    def animate_move(self, before: GameState, after: GameState, move: Move, duration_ms: int) -> None:
        """Anima un movimiento mostrando el estado antes y después con un retardo."""
        self.set_state(before)
        self.highlight_move(move, None)

        def apply_destination() -> None:
            self.set_state(after)
            self.highlight_move(move, None)

        QTimer.singleShot(max(1, duration_ms // 2), apply_destination)


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación Gammy.

    Contiene el tablero, paneles de estado, controles de juego (Start, Pause,
    Step, Back, Reset), selector de escenarios y botón de pruebas.
    """
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Gammy - Gardner Minichess 5x5")
        self.resize(1100, 720)

        self.board_widget = BoardWidget()
        self.state_history: List[GameState] = [initial_state()]
        self.decision_log: List[LoggedDecision] = []
        self.current_index = 0
        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self._auto_step)

        self._build_ui()
        self._refresh_ui()

    def _build_ui(self) -> None:
        """Construye el layout principal: tablero a la izquierda, panel de controles a la derecha."""
        central = QWidget(self)
        layout = QHBoxLayout(central)
        layout.addWidget(self.board_widget, stretch=2)

        right_panel = QVBoxLayout()
        right_panel.addLayout(self._build_status_panel())
        right_panel.addWidget(self._build_controls_panel())
        right_panel.addWidget(self._build_history_panel(), stretch=1)
        right_panel.addWidget(self._build_log_panel(), stretch=1)

        layout.addLayout(right_panel, stretch=3)
        self.setCentralWidget(central)

    def _build_status_panel(self) -> QVBoxLayout:
        """Crea el panel superior con información del turno, evaluación y estado."""
        panel = QVBoxLayout()
        self.turn_label = QLabel("Turn: white")
        self.eval_label = QLabel("Eval (white): 0")
        self.depth_label = QLabel("Depth: 3")
        self.status_label = QLabel("Status: playing")
        self.move_label = QLabel("Move: 0")

        panel.addWidget(self.turn_label)
        panel.addWidget(self.eval_label)
        panel.addWidget(self.depth_label)
        panel.addWidget(self.status_label)
        panel.addWidget(self.move_label)
        return panel

    def _build_controls_panel(self) -> QGroupBox:
        """Crea el panel de controles: botones, profundidad, velocidad y escenarios."""
        group = QGroupBox("Controls")
        layout = QVBoxLayout(group)

        buttons = QHBoxLayout()
        self.start_button = QPushButton("Start")
        self.pause_button = QPushButton("Pause")
        self.step_button = QPushButton("Step")
        self.back_button = QPushButton("Back")
        self.start_button.clicked.connect(self.start_auto)
        self.pause_button.clicked.connect(self.pause_auto)
        self.step_button.clicked.connect(self.step_forward)
        self.back_button.clicked.connect(self.step_back)
        buttons.addWidget(self.start_button)
        buttons.addWidget(self.pause_button)
        buttons.addWidget(self.step_button)
        buttons.addWidget(self.back_button)
        layout.addLayout(buttons)

        nav_buttons = QHBoxLayout()
        self.to_start_button = QPushButton("To Start")
        self.to_end_button = QPushButton("To End")
        self.reset_button = QPushButton("Reset")
        self.to_start_button.clicked.connect(self.jump_to_start)
        self.to_end_button.clicked.connect(self.jump_to_end)
        self.reset_button.clicked.connect(self.reset_game)
        nav_buttons.addWidget(self.to_start_button)
        nav_buttons.addWidget(self.to_end_button)
        nav_buttons.addWidget(self.reset_button)
        layout.addLayout(nav_buttons)

        form = QFormLayout()
        self.white_depth = QSpinBox()
        self.white_depth.setRange(1, 6)
        self.white_depth.setValue(3)
        self.black_depth = QSpinBox()
        self.black_depth.setRange(1, 6)
        self.black_depth.setValue(3)
        form.addRow("White depth", self.white_depth)
        form.addRow("Black depth", self.black_depth)

        self.speed_slider = QSlider(Qt.Horizontal)
        self.speed_slider.setRange(100, 2000)
        self.speed_slider.setValue(600)
        self.speed_slider.valueChanged.connect(self._update_speed_label)
        self.speed_label = QLabel("Speed: 600 ms")
        form.addRow(self.speed_label)
        form.addRow(self.speed_slider)

        layout.addLayout(form)

        scenario_layout = QHBoxLayout()
        self.scenario_box = QComboBox()
        self.scenario_box.addItem("Initial", "initial")
        for key, scenario in get_scenarios().items():
            self.scenario_box.addItem(f"{scenario.name}: {scenario.description}", key)
        self.load_scenario_button = QPushButton("Load Scenario")
        self.load_scenario_button.clicked.connect(self.load_scenario)
        scenario_layout.addWidget(self.scenario_box)
        scenario_layout.addWidget(self.load_scenario_button)
        layout.addLayout(scenario_layout)

        tests_layout = QHBoxLayout()
        self.run_tests_button = QPushButton("Run Tests")
        self.run_tests_button.clicked.connect(self.run_tests)
        tests_layout.addWidget(self.run_tests_button)
        layout.addLayout(tests_layout)

        return group

    def _build_history_panel(self) -> QGroupBox:
        """Crea el panel de historial de movimientos de la partida."""
        group = QGroupBox("Move History")
        layout = QVBoxLayout(group)
        self.history_list = QListWidget()
        layout.addWidget(self.history_list)
        return group

    def _build_log_panel(self) -> QGroupBox:
        """Crea el panel de log de decisiones de la IA."""
        group = QGroupBox("Decision Log")
        layout = QVBoxLayout(group)
        self.log_output = QPlainTextEdit()
        self.log_output.setReadOnly(True)
        layout.addWidget(self.log_output)
        return group

    def start_auto(self) -> None:
        """Inicia el modo automático donde la IA juega ambos lados."""
        if not self.auto_timer.isActive():
            self.auto_timer.start(self.speed_slider.value())

    def pause_auto(self) -> None:
        """Pausa el modo automático."""
        if self.auto_timer.isActive():
            self.auto_timer.stop()

    def _auto_step(self) -> None:
        if not self.step_forward():
            self.pause_auto()

    def step_forward(self) -> bool:
        """Avanza un movimiento. Calcula con la IA si es el último estado conocido."""
        state = self.state_history[self.current_index]
        terminal, _, _ = get_terminal_status(state)
        if terminal:
            return False

        if self.current_index < len(self.state_history) - 1:
            self.current_index += 1
            self._refresh_ui()
            return True

        depth = self.white_depth.value() if state.turn == "white" else self.black_depth.value()
        decision = choose_best_move(state, depth, state.turn)
        if not decision.move:
            return False

        next_state = apply_move(state, decision.move, validate=True)
        self.state_history.append(next_state)
        self.decision_log.append(
            LoggedDecision(decision.move, decision.value, decision.nodes)
        )
        self.current_index += 1

        self.board_widget.animate_move(state, next_state, decision.move, 300)
        self._refresh_ui(skip_board=True)
        return True

    def step_back(self) -> None:
        """Retrocede un movimiento en el historial."""
        if self.current_index > 0:
            self.current_index -= 1
            self._refresh_ui()

    def jump_to_start(self) -> None:
        self.current_index = 0
        self._refresh_ui()

    def jump_to_end(self) -> None:
        self.current_index = len(self.state_history) - 1
        self._refresh_ui()

    def reset_game(self) -> None:
        """Reinicia la partida al estado inicial."""
        self.state_history = [initial_state()]
        self.decision_log = []
        self.current_index = 0
        self.history_list.clear()
        self.log_output.clear()
        self._refresh_ui()

    def load_scenario(self) -> None:
        """Carga el escenario seleccionado en el combo box."""
        data = self.scenario_box.currentData()
        if data == "initial":
            self.reset_game()
            return
        scenario = get_scenarios()[data]
        self.state_history = [scenario.state.clone()]
        self.decision_log = []
        self.current_index = 0
        self.history_list.clear()
        self.log_output.clear()
        self._refresh_ui()

    def run_tests(self) -> None:
        """Ejecuta todas las pruebas y muestra los resultados en el log."""
        results = run_all_tests(depth=3)
        lines = []
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            move_text = move_to_notation(result.move) if result.move else "none"
            lines.append(
                f"{result.name} - {status} | {result.description} | move={move_text}"
            )
            lines.append(
                f"  expected={result.expected} | obtained={result.obtained}"
            )
            lines.append(
                f"  eval_before={result.eval_before:.2f} eval_after={result.eval_after:.2f}"
            )
            lines.append("  state:")
            for row in result.state_lines:
                lines.append(f"    {row}")
        self.log_output.setPlainText("\n".join(lines))

    def _update_speed_label(self) -> None:
        self.speed_label.setText(f"Speed: {self.speed_slider.value()} ms")
        if self.auto_timer.isActive():
            self.auto_timer.start(self.speed_slider.value())

    def _refresh_ui(self, skip_board: bool = False) -> None:
        """Actualiza toda la interfaz: tablero, etiquetas de estado, historial y log."""
        state = self.state_history[self.current_index]
        if not skip_board:
            self.board_widget.set_state(state)

        eval_value = evaluate_state(state, "white")
        self.turn_label.setText(f"Turn: {state.turn}")
        self.eval_label.setText(f"Eval (white): {eval_value:.2f}")
        depth = self.white_depth.value() if state.turn == "white" else self.black_depth.value()
        self.depth_label.setText(f"Depth: {depth}")
        self.move_label.setText(f"Move: {self.current_index}")

        terminal, winner, reason = get_terminal_status(state)
        if terminal:
            if reason == "checkmate":
                self.status_label.setText(f"Status: checkmate ({winner})")
            else:
                self.status_label.setText(f"Status: draw ({reason})")
        else:
            self.status_label.setText("Status: playing")

        last_move = None
        if self.current_index > 0:
            last_move = self.state_history[self.current_index].move_history[-1]

        check_square = None
        if is_in_check(state, state.turn):
            from .engine import find_king

            check_square = find_king(state, state.turn)
        self.board_widget.highlight_move(last_move, check_square)

        self._refresh_history()
        self._refresh_log()

    def _refresh_history(self) -> None:
        self.history_list.clear()
        for move in self.state_history[self.current_index].move_history:
            self.history_list.addItem(move_to_notation(move))

    def _refresh_log(self) -> None:
        self.log_output.clear()
        for entry in self.decision_log:
            text = f"{move_to_notation(entry.move)} | eval={entry.value:.2f} nodes={entry.nodes}"
            self.log_output.appendPlainText(text)


def run() -> None:
    """Punto de entrada de la interfaz gráfica. Crea la aplicación Qt y muestra la ventana."""
    app = QApplication([])
    window = MainWindow()
    window.show()
    app.exec()
