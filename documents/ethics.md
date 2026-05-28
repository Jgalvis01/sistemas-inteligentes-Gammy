# Ética del Sistema — Agente Gammy

> "No existen soluciones perfectas, solo decisiones informadas bajo restricciones, justificadas técnicamente y asumidas éticamente."

---

## 1. Decisiones — ¿Qué autonomía tiene el sistema?

Gammy tiene una autonomía limitada y acotada. Dentro de una partida, el agente decide de forma autónoma qué movimiento realizar en cada turno, basándose en el algoritmo Minimax con poda Alfa-Beta y su función heurística. Sin embargo, esa autonomía está completamente restringida por las reglas del juego y los parámetros definidos por el equipo (pesos de la heurística, profundidad de búsqueda).

Fuera del tablero, Gammy no decide nada. Un humano siempre controla cuándo inicia, pausa, retrocede o reinicia la partida, además de configurar la profundidad de búsqueda y la velocidad de juego. El agente no tiene memoria entre partidas ni capacidad de modificar su propio comportamiento.

---

## 2. Riesgos — ¿Qué consecuencias existen si el agente falla?

Se identifican dos tipos de fallo posibles:

**Fallo técnico:** Si la heurística está mal calibrada, Gammy puede tomar decisiones que parecen buenas localmente pero resultan perjudiciales a largo plazo; por ejemplo, capturar una pieza pero quedar expuesto a un jaque mate en el turno siguiente. Una profundidad de búsqueda baja también limita su capacidad de anticipar consecuencias.

**Consecuencias del fallo:** Al tratarse de un juego, las consecuencias de cualquier fallo son triviales, simplemente se pierde la partida. No existe riesgo real para ninguna persona. Gammy es un sistema de bajo riesgo, muy distinto a agentes de IA aplicados en contextos críticos como medicina, finanzas o conducción autónoma.

Durante el desarrollo no se identificaron fallos graves en el comportamiento del agente más allá de los esperables por limitaciones de profundidad.

---

## 3. Sesgos — ¿Qué prejuicios pueden emerger del diseño?

La heurística de Gammy introduce sesgos inherentes al diseño:

- **Sesgo hacia el material:** Como el criterio de material tiene un peso dominante, Gammy tiende a priorizar capturar piezas sobre otras consideraciones estratégicas, lo que no siempre representa la jugada óptima.

- **Sesgo de centralidad fijo:** Las casillas centrales valoradas por el agente (b2–d4) están definidas de forma fija en el código (`constants.py`). Gammy siempre considera esas casillas importantes sin importar el momento de la partida, aunque en ciertas situaciones el control del centro sea irrelevante.

- **Sesgo de intuición humana:** Los pesos de la heurística fueron definidos por el equipo basándose en conocimiento general del ajedrez, no mediante entrenamiento con datos reales de partidas. Esto significa que reflejan la intuición del equipo sobre lo que es una buena posición en un tablero 5×5, lo cual puede no ser óptimo.

---

## 4. Impacto — ¿Cómo afecta el despliegue a los humanos?

**Impacto positivo:**
Gammy puede funcionar como oponente de práctica para quienes quieran aprender Gardner Minichess. Su interfaz muestra el historial de movimientos y los registro de decisiones con la evaluación de cada jugada, lo que lo convierte en una herramienta transparente y educativa para entender cómo razona un agente de IA en juegos estratégicos.

**Impacto limitado:**
Al ser un agente para un juego de nicho en un tablero reducido, su impacto real en la sociedad es mínimo. No reemplaza empleos, no toma decisiones sobre personas, no tiene acceso a datos privados y no presenta riesgos de uso indebido. Su alcance está completamente contenido dentro del contexto de juego para el que fue diseñado.

---

## Reflexión Final

Gammy es un sistema técnicamente funcional y éticamente responsable dentro de su dominio. Las decisiones de diseño, como la elección del algoritmo, la definición de la heurística y los parámetros de evaluación, fueron tomadas conscientemente por el equipo, asumiendo sus limitaciones y siendo transparentes sobre ellas. El uso de herramientas de IA generativa (ChatGPT Codex para el código, Claude para la documentación) fue declarado explícitamente y todos los resultados fueron revisados y validados por los integrantes del equipo.