"""Constantes del juego Gardner Minichess 5x5.

Define las dimensiones del tablero, los tipos de piezas con sus valores,
los pesos de la función de evaluación heurística, y las direcciones de
movimiento para cada tipo de pieza.
"""

# Dimensión del tablero (5x5 para Gardner Minichess)
BOARD_SIZE = 5

# Colores de los jugadores
COLORS = ("white", "black")

# Tipos de piezas: P=Peón, C=Caballo, A=Alfil, T=Torre, Q=Reina, K=Rey
PIECE_TYPES = ("P", "C", "A", "T", "Q", "K")

# Valor material de cada pieza (usado por la función de evaluación)
PIECE_VALUES = {
    "P": 1,      # Peón
    "C": 3,      # Caballo
    "A": 3,      # Alfil
    "T": 5,      # Torre
    "Q": 9,      # Reina
    "K": 1000,   # Rey (valor alto para priorizar su protección)
}

# Piezas a las que un peón puede promocionar al llegar a la última fila
PROMOTION_CHOICES = ("Q", "T", "A", "C")

# Pesos de cada componente de la función de evaluación heurística
WEIGHTS = {
    "material": 0.40,      # Ventaja material (piezas propias vs oponente)
    "center": 0.25,        # Control de las casillas centrales del tablero
    "king_safety": 0.20,   # Seguridad del rey (piezas aliadas adyacentes)
    "mobility": 0.15,      # Movilidad (cantidad de movimientos legales)
}

# Casillas centrales del tablero 5x5 (las 9 del centro)
CENTER_SQUARES = {
    (1, 1), (1, 2), (1, 3),
    (2, 1), (2, 2), (2, 3),
    (3, 1), (3, 2), (3, 3),
}

# Desplazamientos del rey (las 8 casillas adyacentes)
KING_OFFSETS = [
    (-1, -1), (-1, 0), (-1, 1),
    (0, -1), (0, 1),
    (1, -1), (1, 0), (1, 1),
]

# Desplazamientos del caballo (movimiento en "L")
KNIGHT_OFFSETS = [
    (-2, -1), (-2, 1),
    (-1, -2), (-1, 2),
    (1, -2), (1, 2),
    (2, -1), (2, 1),
]

# Direcciones ortogonales (torre y reina) y diagonales (alfil y reina)
DIR_ORTHO = [(-1, 0), (1, 0), (0, -1), (0, 1)]
DIR_DIAG = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

# Coordenadas algebraicas del tablero (columnas a-e, filas 1-5)
FILES = ["a", "b", "c", "d", "e"]
RANKS = ["1", "2", "3", "4", "5"]
