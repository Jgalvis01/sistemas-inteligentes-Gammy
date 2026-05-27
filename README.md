# Gammy - Gardner Minichess 5x5

Gammy es un agente de inteligencia artificial adversarial que juega Gardner Minichess, una variante compacta del ajedrez de 5×5 donde cada lado comienza con un conjunto completo de piezas (rey, reina, torre, alfil, caballo y cinco peones). El agente utiliza algoritmos clásicos de búsqueda para seleccionar el mejor movimiento en cada turno.

## Equipo

- Valeria Gustin
- Jeysa Blandón
- Sara Tabares
- Julian Galvis
- Santiago Salazar

## Descripción del problema

Gardner Minichess es una variante del ajedrez que se juega en un tablero de 5×5. Cada jugador controla hasta 10 piezas y el movimiento de las piezas sigue las reglas estándar del ajedrez. El tamaño reducido del tablero hace que el juego sea manejable para agentes basados en búsqueda, mientras conserva la profundidad táctica que hace desafiante al ajedrez.

El problema central es la toma de decisiones adversariales bajo incertidumbre: en cada turno, el agente debe elegir un movimiento que maximice su propia ventaja mientras anticipa las mejores respuestas del oponente. El espacio de estados, aunque más pequeño que el del ajedrez estándar, sigue siendo lo suficientemente grande como para requerir búsqueda inteligente y técnicas de poda.

## Instalación y ejecución

1) Instalar dependencias

```
pip install -r requirements.txt
```

2) Ejecutar la interfaz gráfica (GUI)

```
python proyecto.py
```

3) Ejecutar pruebas desde la consola

```
python proyecto.py --tests
```

## Estructura del Agente

- gammy/engine.py: Reglas, generación de movimientos y detección de final de partida
- gammy/ai.py: Minimax con poda alfa-beta y heurística
- gammy/gui.py: Interfaz en PySide6 y controles de simulación
- gammy/tests.py: Seis escenarios y ejecutor de pruebas
- proyecto.py: Punto de entrada CLI

## Justificación técnica

**¿Por qué Minimax con poda Alfa-Beta?**

Gardner Minichess es un juego de suma cero, de información perfecta y para dos jugadores: exactamente el tipo de entorno para el cual fue diseñado el algoritmo Minimax. La poda Alfa-Beta elimina ramas que no pueden afectar la decisión final, permitiendo que el agente alcance mayores profundidades de búsqueda sin requerir cómputo adicional. A profundidad 4, Alfa-Beta normalmente explora muchos menos nodos que Minimax puro, mientras devuelve el mismo movimiento óptimo.

**¿Por qué esta heurística?**

La función heurística del agente combina cuatro criterios ponderados:

```
h(s) = wM·fM(s) + wC·fC(s) + wK·fK(s) + wMov·fMov(s)
```

Dado que no es viable realizar una búsqueda exhaustiva hasta estados terminales en cada turno, la heurística aproxima la calidad de una posición. Los cuatro criterios (material, control del centro, seguridad del rey y movilidad) están bien establecidos en la literatura de IA aplicada al ajedrez y representan los aspectos más decisivos de una posición en Gardner Minichess. Su combinación ponderada permite que Gammy equilibre ganancias materiales a corto plazo con fortaleza posicional a largo plazo.

## Metodología de Evaluación

- **Tasa de victoria:** porcentaje de partidas ganadas contra un agente aleatorio y un agente voraz.
- **Nodos explorados:** comparación entre Minimax puro y con poda Alfa-Beta a igual profundidad.
- **Profundidad vs. tiempo:** resultados comparados en profundidades 1, 2 y 3.
- **Escenarios de prueba:** seis casos predefinidos en `tests.py` (jaque mate en 1, capturas forzadas, detección de empate).

## Declaración sobre el uso de IA generativa

Este proyecto utilizó ChatGPT Codex y Claude como asistentes de desarrollo. La IA generativa se utilizó para apoyar en:

- La estructura inicial y depuración de la implementación de Minimax y Alfa-Beta.
- La redacción y mejora de la documentación escrita (README, informe y archivo de ética).
- La revisión de la lógica de generación de movimientos para detectar casos límite.
- La generación de ideas para escenarios de prueba.

Todos los resultados generados por IA fueron revisados, validados y adaptados por el equipo. Las decisiones finales sobre la arquitectura, el diseño de la heurística y la metodología de evaluación fueron tomadas por los integrantes del equipo.

## Notas

- El enroque es solo un marcador de posición (no se usa en Gardner).
- La captura al paso (en passant) no está implementada para Gardner.
- La promoción de peón está implementada a Q/T/A/C.
- El empate por la regla de 50 movimientos se basa en movimientos sin capturas.
