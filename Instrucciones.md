Operación Dino Crash (EDA conceptual)
Introducción a la Misión
Agentes, el cuartel general quiere que piensen como *analistas de datos: qué dataset haría falta, qué preguntas hacerle a los datos y, solo después de entenderlos, qué tipo de modelo de IA tendría sentido.

Contexto: el juego del dinosaurio de Chrome (Dino Run) — el que aparece sin internet.

Reglas de esta operación:

No se entrega código. Solo análisis escrito (reporte en Markdown).
Justifica cada respuesta con razonamiento sobre forma de los datos, no con intuición vaga.
Usa tablas, listas y mini-ejemplos numéricos cuando ayuden.
Entregable único: reporte_dino_crash_eda.md

¿Qué es EDA y por qué va antes del modelo?
Datos crudos  →  EDA (entender)  →  Decisión de modelo  →  (luego) entrenar

Si eliges el modelo primero, corres el riesgo de usar un martillo
para un tornillo: datos desbalanceados, variables mal definidas,
o un problema que no era clasificación sino regresión.
Bloque 1 — ¿Qué dataset necesitamos?
Misión 1: Definir el problema y el dataset ideal
La Historia
Antes de “predecir algo”, hay que decidir qué pregunta respondes y qué fila representa cada observación.

Escenarios posibles (elige analizar los tres en el reporte)
ID	Pregunta de negocio / juego	¿Una fila = qué?
P1	¿Morirá en el siguiente frame?	Un frame de una partida
P2	¿Cuántos puntos alcanzará esta partida al morir?	Una partida completa
P3	¿Qué tipo de obstáculo viene próximo?	Un frame o un evento
Tu Tarea (escrito)
Para cada escenario P1, P2 y P3:

Variable objetivo (Y): ¿qué columna sería? ¿tipo? (numérica, categórica, binaria).
Variables de entrada (X): lista mínimo 5 columnas que pedirías y por qué cada una.
Granularidad: ¿necesitas un frame cada 16 ms, cada salto, o un resumen por partida?
Tamaño mínimo razonable: ¿cuántas filas o partidas harían falta para confiar? Argumenta.
Riesgo si el dataset está mal definido: un error de diseño y su consecuencia.
Misión 2: Diccionario de datos (qué debe traer el CSV)
La Historia
Interceptaste un borrador de telemetría. Revisa si alcanza para P1 o si le falta algo.

Columnas propuestas
Columna	Tipo sugerido	Descripción breve
session_id	entero	ID de partida
frame	entero	Índice del frame en la partida
time_ms	entero	Tiempo desde que empezó la partida
score	entero	Puntuación en pantalla
speed	numérico	Velocidad del escenario
obstacle_type	categórica	none, cactus_small, cactus_large, bird
dist_obstacle	numérico	Distancia al próximo obstáculo (px)
jump	binaria 0/1	¿El dino está saltando?
died	binaria 0/1	1 solo en el último frame de la sesión
Muestra para analizar (10 filas — sesión 7)
frame	timems	score	speed	obstacletype	distobstacle	jump	died
0	0	0	6.0	none	180	0	0
40	640	8	6.4	none	165	0	0
80	1280	16	6.8	cactussmall	55	1	0
81	1296	16	6.8	cactussmall	38	1	0
82	1312	16	6.8	cactussmall	12	0	1
0	0	0	6.0	none	200	0	0
120	1920	24	7.2	bird	48	1	0
200	3200	40	8.0	none	150	0	0
280	4480	56	8.8	cactuslarge	22	0	1
50	800	10	6.5	cactussmall	90	0	0
(Filas 1–5: misma sesión que termina en frame 82; filas 6–9: otras sesiones resumidas.)

Tu Tarea (escrito)
¿Qué patrón ves en la fila donde died=1 (frame 82)?
¿=score= es buena variable para predecir muerte en el siguiente frame? ¿Por qué sí o no?
¿Falta alguna columna crítica para P1? (pista: altura del dino, agachado, lag de reacción del jugador…)
¿=died= tal como está definida sirve para P1 o solo describe el final de la partida?