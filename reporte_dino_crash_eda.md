# Operación Dino Crash: reporte de EDA conceptual

## Introducción

El análisis exploratorio de datos (EDA) permite revisar qué representa cada fila, cómo se distribuyen las variables, qué información falta y si las etiquetas responden a la pregunta planteada. Debe realizarse antes de elegir un modelo: una predicción de muerte requiere una etiqueta binaria futura; una predicción de puntos requiere una cantidad numérica; identificar un obstáculo requiere categorías.

El orden de trabajo es **datos crudos → EDA → decisión de modelo → entrenamiento**. Este reporte propone datasets y analiza las diez filas entregadas. Los tamaños de muestra son metas iniciales de recolección, no garantías estadísticas; no se entrenó ningún modelo ni se observaron datos adicionales.

## Misión 1. Definir el problema y el dataset ideal

### P1. ¿Morirá en el siguiente frame?

**Objetivo Y:** `death_next_frame`, variable binaria: 1 si un dinosaurio vivo en el frame actual muere en el frame inmediatamente siguiente; 0 si sobrevive a ese frame. La observación se captura después de actualizar el estado actual, antes de conocer el siguiente.

**Una fila:** un frame de una partida, identificado por `session_id` y `frame`. Conviene registrar cada actualización del juego, aproximadamente cada 16 ms en el supuesto de la actividad, y conservar el intervalo real. Registrar únicamente saltos perdería los estados inmediatamente anteriores a una colisión.

| Entrada X | Razón para solicitarla |
|---|---|
| `dist_obstacle` | Mide la separación horizontal disponible antes de una posible colisión. |
| `speed` | Una misma distancia supone diferente tiempo de reacción según la velocidad. |
| `dino_y` | La altura permite distinguir si el dinosaurio está por encima del obstáculo. |
| `dino_vy` | Distingue ascenso y descenso a igual altura. |
| `duck` | Agacharse modifica la zona del dinosaurio que puede colisionar. |
| `obstacle_type` | Diferencia categorías con geometrías distintas. |
| `obstacle_width`, `obstacle_height`, `obstacle_y` | Describen la extensión y posición del obstáculo, especialmente si es un ave. |
| `action_current` | Registra la orden ya conocida al predecir: saltar, agacharse o ninguna. |
| `delta_time_ms` | Permite interpretar el desplazamiento entre actualizaciones cuando cambia su duración. |

Las entradas solo pueden contener información disponible en el instante de predicción. Las acciones futuras desconocidas añaden incertidumbre y no deben incorporarse retrospectivamente.

**Tamaño inicial razonable:** 1,000 partidas completas con muerte registrada. Si cada una aporta 1,000 frames utilizables, habría alrededor de un millón de filas, pero solo unos 1,000 positivos: aproximadamente 0.1 %. Siempre predecir supervivencia obtendría cerca de 99.9 % de exactitud y aun así fallaría todas las muertes. Por eso importa reunir muertes en diferentes velocidades, obstáculos y estilos de juego, además de filas totales. Una reserva del 20 % de partidas contendría aproximadamente 200 positivos, todavía limitada para evaluar situaciones raras. La suficiencia se revisaría con curvas de aprendizaje e incertidumbre de las métricas.

**Error de diseño y consecuencia:** usar `died` del mismo frame como objetivo convertiría la tarea en reconocer una muerte ya ocurrida. También deben separarse las partidas entre entrenamiento y evaluación: frames vecinos de una misma partida son muy parecidos y producirían una evaluación demasiado favorable si se repartieran al azar.

### P2. ¿Cuántos puntos alcanzará esta partida al morir?

**Objetivo Y:** `final_score`, cantidad numérica entera. Es una tarea de regresión porque interesa la magnitud de la puntuación y del error, no una clase.

**Una fila:** una partida completa. Para que la predicción sea útil, se fija un instante de predicción: el comienzo de la partida. El resumen final proporciona Y, mientras que X contiene exclusivamente información disponible al inicio. Esto permite incluir partidas que terminan muy pronto sin excluirlas por no alcanzar un punto de observación posterior.

| Entrada X | Razón para solicitarla |
|---|---|
| `initial_speed` | Define la velocidad con la que comienza la dificultad. |
| `difficulty_setting` | Distingue configuraciones que pueden cambiar la distribución de puntuaciones. |
| `game_version` | Identifica cambios de reglas o física que pueden afectar la duración. |
| `input_device` | Permite investigar diferencias asociadas con teclado, pantalla táctil u otros controles. |
| `prior_games_count` | Resume la experiencia previa registrada del jugador. |
| `prior_score_median` | Resume su desempeño en partidas anteriores, sin usar la actual ni posteriores. |
| `prior_reaction_ms_median` | Resume tiempos de reacción históricos que podrían relacionarse con la supervivencia. |

Si versión o dificultad son constantes, no aportarán variación predictiva dentro de ese dataset. Los jugadores nuevos tendrán históricos ausentes: se debe marcar esa condición y evitar sustituirlos por información futura. Los identificadores sirven para agrupar y auditar, no como medidas de habilidad.

**Granularidad:** un resumen por partida, con antecedentes calculados antes de su inicio. No hacen falta todos los frames como filas del dataset final de P2.

**Tamaño inicial razonable:** 2,000 partidas de al menos 100 jugadores, procurando diversidad de experiencia. Una prueba del 20 % aportaría unas 400 partidas para examinar errores absolutos y su dispersión. Sin embargo, muchas partidas del mismo jugador no equivalen a observaciones independientes. Para generalizar a jugadores nuevos se separarían jugadores completos; para predecir futuras partidas de jugadores conocidos se usaría una separación temporal. Si existen pocas puntuaciones muy altas, se necesitaría ampliar esa cobertura.

**Error de diseño y consecuencia:** incluir duración final, número total de saltos o velocidad al morir filtraría información del desenlace. El modelo parecería preciso, pero esas columnas no existirían al comenzar la partida. Una partida abandonada tampoco debe etiquetarse como muerte: su puntuación final de muerte es desconocida.

### P3. ¿Qué tipo de obstáculo viene próximo?

**Objetivo Y:** `next_obstacle_type`, variable categórica con clases `cactus_small`, `cactus_large` y `bird`. Se propone predecir el próximo obstáculo que aparecerá, antes de que sea visible. `none` describe ausencia de un obstáculo visible; no es un tipo del próximo obstáculo que efectivamente aparece.

**Una fila:** un evento de predicción después de superar un obstáculo y antes de observar el siguiente. El registro posterior de la aparición aporta la etiqueta. Si el siguiente ya es visible, identificarlo sería otra tarea y necesitaría una definición distinta.

| Entrada X | Razón para solicitarla |
|---|---|
| `speed` | Permite explorar si las frecuencias de aparición cambian con la velocidad. |
| `elapsed_time_ms` | Sitúa el evento dentro del avance de la partida. |
| `previous_obstacle_type` | Permite investigar dependencias entre tipos consecutivos. |
| `second_previous_obstacle_type` | Ayuda a examinar patrones de secuencia más largos. |
| `previous_gap_px` | Describe una separación ya observada, que podría depender de las reglas de generación. |
| `obstacles_passed_count` | Mide el avance en términos de obstáculos superados. |
| `game_version` | Permite separar posibles diferencias en las reglas de aparición. |

Estas variables son hipótesis para el EDA, no evidencia de que la secuencia sea predecible. Si la generación es aleatoria e independiente del historial, este no permitirá anticipar el resultado individual con precisión.

**Granularidad:** un registro por evento evita repetir decenas de veces la misma etiqueta mientras se aproxima un único obstáculo. Se necesita un `event_id` y el identificador de partida para reconstruir la secuencia.

**Tamaño inicial razonable:** 3,000 eventos distribuidos entre al menos 300 partidas, procurando un mínimo de 300 ejemplos por categoría. Si las aves representaran solo el 5 %, harían falta aproximadamente 6,000 eventos para reunir 300 aves en promedio. Se conservaría la frecuencia natural en evaluación y se examinarían resultados por clase; una cantidad total grande no compensa una categoría casi ausente.

**Error de diseño y consecuencia:** incluir el tipo, imagen o geometría del obstáculo futuro en X revelaría la respuesta. Si la partida acaba antes de observar su aparición, el evento queda sin etiqueta; no se convierte automáticamente en `none`.

## Misión 2. Revisar el diccionario de datos y la muestra

### Diccionario revisado para P1

El CSV propuesto aporta contexto, pero no alcanza para construir con fiabilidad todas las etiquetas de P1 ni describir la geometría de colisión.

| Columna | Tipo | Definición y validación necesarias |
|---|---|---|
| `session_id` | Entero o identificador | Identifica una partida sin reutilizar el valor en reinicios. Es obligatorio en cada fila. |
| `frame` | Entero | Índice creciente dentro de la partida. La pareja con `session_id` debe ser única. |
| `time_ms` | Entero | Tiempo transcurrido, no negativo y creciente. Permite detectar pausas o huecos. |
| `score` | Entero | Puntuación actual, no la final. Puede repetirse entre frames próximos. |
| `speed` | Numérico | Velocidad actual; documentar si está en px/frame, px/s u otra unidad interna. |
| `obstacle_type` | Categórico | Usar exactamente `none`, `cactus_small`, `cactus_large` o `bird`. |
| `dist_obstacle` | Numérico nullable | Distancia horizontal entre bordes definidos de las cajas de colisión. Si no hay obstáculo, usar ausente y explicar su significado. |
| `jump` | Binario | Estado actual de salto; distinguirlo de la pulsación de la tecla de salto. |
| `died` | Binario | 1 si la muerte ocurre en este frame; un cierre voluntario no debe marcarse como muerte. |
| `death_next_frame` | Binario nullable | Objetivo derivado del frame inmediatamente posterior de la misma partida. Ausente si no puede verificarse. |

Además de las entradas geométricas de P1, conviene solicitar estas columnas:

| Columna adicional | Tipo | Utilidad |
|---|---|---|
| `dino_y`, `dino_vy` | Numéricas | Separan altura y movimiento vertical; `jump=1` no describe ambas cosas. |
| `duck` | Binario | Indica la postura agachada. |
| `dino_hitbox_width`, `dino_hitbox_height` | Numéricas | Describen las dimensiones efectivas de colisión. |
| `obstacle_id` | Identificador | Permite saber si dos distancias sucesivas se refieren al mismo objeto. |
| `obstacle_width`, `obstacle_height`, `obstacle_y` | Numéricas | Permiten comparar la posición y tamaño del obstáculo con el dinosaurio. |
| `action_current`, `time_since_last_input_ms` | Categórica y numérica | Describen órdenes ya emitidas y su antigüedad. |
| `prior_reaction_ms_median` | Numérica nullable | Estima el retraso habitual con reacciones ya observadas; no usa la respuesta futura al obstáculo actual. |
| `delta_time_ms` | Numérica | Registra la duración real entre actualizaciones. |
| `session_end_reason` | Categórica | Distingue muerte, abandono y corte de captura; sirve para validar etiquetas, no como entrada predictiva. |

Si varios obstáculos pueden colisionar durante el siguiente frame, registrar solo uno podría ser insuficiente. La telemetría tendría que representar todos los obstáculos relevantes y sus posiciones.

### Calidad y consistencia de las diez filas

1. **La identificación de partidas es insuficiente.** El título menciona la sesión 7, pero la nota atribuye las filas 6–9 a otras sesiones y la muestra omite `session_id`. El frame vuelve a 0 después del 82; la última fila, con frame 50, tampoco tiene una pertenencia aclarada. No se deben unir estos registros como una sola secuencia.
2. **Hay saltos de muestreo.** Los frames 0, 40 y 80 no son consecutivos. En esas filas, desplazar la etiqueta a la siguiente fila significaría predecir a 640 ms, no al siguiente frame. Solo los pares 80→81 y 81→82 permiten verificar directamente el horizonte solicitado en la primera partida.
3. **Falta normalizar nombres y categorías.** La muestra usa `timems`, `obstacletype` y `distobstacle`, frente a `time_ms`, `obstacle_type` y `dist_obstacle`. También usa `cactussmall` y `cactuslarge`; deben homologarse con el diccionario para no crear categorías artificiales.
4. **Hay distancias positivas cuando el tipo es `none`.** Por ejemplo, el frame 0 tiene distancia 180. Debe aclararse si se mide un objeto fuera de pantalla o si es un valor de relleno. Con la definición de ausencia de obstáculo, esa distancia sería un dato ausente, no una separación física observada.
5. **La unidad de velocidad necesita aclaración.** Entre los frames 80 y 81 la distancia disminuye 17 px; entre 81 y 82 disminuye 26 px, aunque `speed=6.8` permanece constante. No puede concluirse que haya un error sin conocer unidades, objeto seguido y referencia de distancia; sí corresponde auditarlo.
6. **El tiempo es compatible con el supuesto de la actividad.** En las filas mostradas, `time_ms = frame × 16`. Esto indica una relación consistente en la muestra, pero no garantiza que la captura completa carezca de frames perdidos.

Las dos muertes entre diez filas equivalen al 20 % de esta selección. Como mezcla fragmentos y partidas resumidas, esa proporción no estima la frecuencia real de muerte por frame.

### ¿Qué patrón aparece al morir en el frame 82?

| Frame | Distancia | Salto | Velocidad | Puntos | Muerte actual |
|---|---:|---:|---:|---:|---:|
| 80 | 55 | 1 | 6.8 | 16 | 0 |
| 81 | 38 | 1 | 6.8 | 16 | 0 |
| 82 | 12 | 0 | 6.8 | 16 | 1 |

El cactus pequeño se aproxima y, en el registro de muerte, el dinosaurio deja de figurar saltando. El patrón es compatible con una colisión cerca del suelo. No demuestra que aterrizar haya causado la muerte: `jump` podría reiniciarse al morir y faltan altura, cajas de colisión y orden de actualización. Tampoco permite afirmar que toda distancia menor que 12 px sea mortal.

La otra fila de muerte presenta cactus grande, distancia 22 y `jump=0`, pero no tiene un frame inmediatamente anterior disponible. Apoya una descripción de proximidad, sin demostrar un umbral ni una regla causal.

### ¿Es `score` una buena entrada para predecir muerte en el siguiente frame?

Puede aportar contexto sobre el avance y su relación con la dificultad, pero es insuficiente por sí sola. Los frames 80, 81 y 82 mantienen 16 puntos mientras cambian la distancia y el desenlace. Además, el frame 80 tiene `death_next_frame=0` y el 81 tiene `death_next_frame=1`: el mismo puntaje corresponde a objetivos distintos.

En esta muestra, el puntaje coincide con `time_ms / 80` redondeado hacia abajo y la velocidad también crece con el avance. Se revisaría si esas variables contienen información redundante. La utilidad adicional de `score` se comprobaría comparando resultados con y sin esa columna sobre partidas separadas. El puntaje actual es una entrada válida si ya está disponible; el puntaje final filtraría información futura.

### ¿Sirve `died` tal como está definida para P1?

Describe el desenlace del frame actual. Puede servir como fuente para construir el objetivo futuro, pero no es directamente la etiqueta solicitada.

Para cada frame vivo t, se consulta `died` del frame t+1 **de la misma partida y con índice consecutivo**. Si falta ese frame, la etiqueta queda desconocida. El frame donde el dinosaurio ya murió se excluye de las observaciones predictivas.

| Frame de entrada | Frame posterior verificado | `died` posterior | `death_next_frame` |
|---|---|---:|---|
| 0 | No está el frame 1 | — | Desconocida |
| 40 | No está el frame 41 | — | Desconocida |
| 80 | 81 | 0 | 0 |
| 81 | 82 | 1 | 1 |
| 82 | Ya murió | — | No aplica |

Nunca debe tomarse el frame 0 de una nueva partida como continuación del frame 82. También debe confirmarse que `died=1` significa muerte real: ser el último registro de un archivo no basta si la captura se interrumpió.

## Decisión de modelo después del EDA

Antes de entrenar se revisarían datos ausentes, duplicados, unidades, continuidad temporal, distribución de objetivos y cobertura de velocidades y obstáculos. Las transformaciones aprendidas de los datos se ajustarían solo con entrenamiento.

| Escenario | Decisión inicial razonada | Evaluación |
|---|---|---|
| P1 | Clasificación binaria. Una regresión logística ofrece una referencia; árboles pueden representar interacciones entre altura, distancia y velocidad. La elección depende del EDA y de la validación. | Precisión y sensibilidad de muerte, curva precisión-recall y calibración; separar partidas completas. |
| P2 | Regresión. Comparar primero con la mediana de puntuación del entrenamiento; después considerar regresión regularizada o árboles según las relaciones observadas. | Error absoluto medio en puntos y errores por nivel de puntuación, con separación temporal o por jugador según el uso. |
| P3 | Clasificación multiclase. Comparar con la clase mayoritaria y frecuencias condicionadas por avance; probar un modelo solo si existen señales disponibles antes de la aparición. | Matriz de confusión y F1 macro por partidas separadas para no ocultar fallos en clases escasas. |

Las diez filas permiten detectar problemas de definición y calidad, pero no elegir un modelo ganador ni estimar su desempeño. La prioridad es capturar partidas identificadas, distinguir estados actuales de etiquetas futuras y fijar el instante exacto en que se realizará cada predicción.
