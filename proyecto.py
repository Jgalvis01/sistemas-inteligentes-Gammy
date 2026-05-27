"""Punto de entrada principal de Gammy - Gardner Minichess 5x5.

Ejecuta la interfaz gráfica por defecto, o las pruebas automáticas
con el argumento --tests.
"""

import argparse

from gammy.gui import run as run_gui
from gammy.model import move_to_notation
from gammy.tests import run_all_tests


def print_test_results() -> None:
    """Ejecuta las pruebas e imprime los resultados en consola."""
	results = run_all_tests(depth=3)
	for result in results:
		status = "PASS" if result.passed else "FAIL"
		move_text = move_to_notation(result.move) if result.move else "none"
		print(f"{result.name} - {status}")
		print(f"  {result.description}")
		print(f"  expected: {result.expected}")
		print(f"  obtained: {result.obtained}")
		print(f"  move: {move_text}")
		print(f"  eval_before: {result.eval_before:.2f}")
		print(f"  eval_after: {result.eval_after:.2f}")
		print("  state:")
		for row in result.state_lines:
			print(f"    {row}")
		print("")


def main() -> None:
    """Función principal: parsea argumentos y lanza la GUI o las pruebas."""
	parser = argparse.ArgumentParser(description="Gammy Gardner Minichess 5x5")
	parser.add_argument(
		"--tests",
		action="store_true",
		help="Run the six test scenarios from the PDFs",
	)
	args = parser.parse_args()

	if args.tests:
		print_test_results()
	else:
		run_gui()


if __name__ == "__main__":
	main()
