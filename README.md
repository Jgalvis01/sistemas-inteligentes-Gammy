# Gammy - Gardner Minichess 5x5

This project implements the Gammy adversarial agent for Gardner Minichess 5x5 using only the rules and heuristics described in the provided PDFs.

## Quick start

1) Install dependencies

```
pip install -r requirements.txt
```

2) Run the GUI

```
python proyecto.py
```

3) Run tests from console

```
python proyecto.py --tests
```

## Project layout

- gammy/engine.py: rules, move generation, and terminal detection
- gammy/ai.py: minimax with alpha-beta and heuristic
- gammy/gui.py: PySide6 interface and simulation controls
- gammy/tests.py: six scenarios and test runner
- proyecto.py: CLI entry point

## Notes

- Castling is a placeholder only (not used in Gardner).
- En passant is not implemented for Gardner.
- Pawn promotion is implemented to Q/T/A/C.
- The 50-move draw is based on moves without captures, per the PDFs.
