           ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
             10 PREGUNTAS REDES NEURONALES CONVOLUCIONALES
                                 (CNN)

                            Eduardo Alcaraz
			           Jose Alberto Ruiz Lopez
           ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


Índice
──────

1. Instrucciones (alumnos)
2. Pregunta 1 — Convolución a mano (3×3)
3. Pregunta 2 — Contar pesos
4. Pregunta 3 — ¿Qué cambia si meto más capas?
5. Pregunta 4 — Formas: de volumen a vector
6. Pregunta 5 — Softmax y el error “casi seguro”
7. Pregunta 6 — Padding, stride y “se me achicó la imagen”
8. Pregunta 7 — Dropout: ¿dónde y para qué?
9. Pregunta 8 — Diseño: 5 clases de animales
10. Pregunta 9 — CNN vs MLP vs RNN (mismo problema, mala herramienta)
11. Pregunta 10 — Experimento mental: mover un gato
12. Autoevaluación rápida (opcional)
13. Notas al pie (fórmulas útiles — no sustituyen el razonamiento)


1 Instrucciones
═════════════════════════

  • Responde *con lápiz y papel* (o en este mismo buffer de Org).
  • No basta con definir de memoria: hay que *calcular*, *comparar* o
    *justificar*.


2 Pregunta 1 — Convolución a mano (3×3)
═══════════════════════════════════════

  Tienes este trozo de imagen en escala de grises (un canal) y este
  kernel:

  ┌────
  │   Imagen 5×5                 Kernel 3×3
  │   0  0  1  0  0              1  0 -1
  │   0  1  2  1  0              1  0 -1
  │   1  2  3  2  1              1  0 -1
  │   0  1  2  1  0
  │   0  0  1  0  0
  └────


2.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌

  1. Con *stride = 1* y *padding valid* (sin relleno), ¿cuál es el
     tamaño del mapa de salida?
     R- Tamaño de salida seria: 5−3/1 + 1 = 3×3.
   
  2. Calcula *solo* el valor de la esquina superior izquierda del mapa
     (la primera posición del filtro). Muestra la suma de productos.
     R- 
     fila 1: 0 0 1
     fila 2: 0 1 2
     fila 3: 1 2 3
     0x1 + 0x0 + 1x(−1) = −1
     0x1 + 1x0 + 2x(−1) = −2
     1x1 + 2x0 + 3x(−1) = -2
     
     Suma de filas -1-2-2 = -5
  3. ¿Este kernel parece detectar bordes *verticales* u *horizontales*?
     Justifica mirando los signos.
     
     R- Detecta bordes verticales, donde cada fila del kernel es 1, 0, −1, y eso se resta a lo de la derecha a lo de la izquierda. Se activa cuando hay un cambio del brillo de izquierda a      	derecha, haciendo que se haga una linea o borde vertical


3 Pregunta 2 — Contar pesos
═══════════════════════════

  Una imagen RGB de *28×28×3*. Compara dos modelos:

  • *Modelo A (MLP ingenuo):* aplastas la imagen a un vector y conectas
    *todas* las entradas a una capa densa de *64 neuronas* (sin bias por
    ahora).
  • *Modelo B (CNN):* una `Conv2D' con *16 filtros* de *3×3*,
    `padding''same'=, sobre la misma imagen (con bias: un bias por
    filtro).


3.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌

  1. ¿Cuántos pesos tiene la capa densa del Modelo A? (fórmula y número)
     R- En el modelo A tenemos 28x28x3, que da un total 2352 entradas. Eso lo multiplicamos por la 
	cantidad de neuronas para obtener la cantidad de pesos. 2352 × 64 da un total de 150,528 pesos.
  2. ¿Cuántos parámetros tiene la Conv2D del Modelo B? (pesos de kernels
     + biases)
     R- En el modelo B tenemos 3x3x3x16 lo que da un total 432 pesos, más los 16 filtros (biases), 
	en total serian 448 parámetros.
  3. En *una frase*: ¿por qué la CNN suele generalizar mejor con el
     mismo número de imágenes de entrenamiento?
     R- La CNN reutiliza los mismos pesos de la imagen, tiene muchos menos parámetros para ajustar, 
	entonces le cuesta menos memorizar y tiende a generalizar mejor.


4 Pregunta 3 — ¿Qué cambia si meto más capas?
═════════════════════════════════════════════

  Parte del notebook `CNNriesgo' (simplificado):

  ┌────
  │   Entrada (21×28×3)
  │     → Conv2D(32, 3×3, same) + LeakyReLU
  │     → MaxPool(2×2)
  │     → Flatten → Dense(32) → Dense(nClasses, softmax)
  └────

  Quieres *apilar un segundo bloque* convolucional *antes* del Flatten:

  ┌────
  │   … → Conv2D(32) → Pool → Conv2D(64, 3×3, same) → Pool → Flatten → …
  └────


4.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌

  1. Tras el *primer* MaxPool(2×2) con padding same sobre 21×28, ¿qué
     tamaño aproximado (alto×ancho) esperas? (puedes redondear / usar la
     regla “casi la mitad”)
     R- 21×28 con maxpool 2×2 y same da 21/2 × 28/2, entonces el tamano aproximado seria de 11×14
  2. ¿Qué *significan* ahora los 64 filtros de la segunda Conv2D:
     detectan bordes “crudos” o patrones *más compuestos*? Explica con
     la analogía de la lupa / capas abstractas.
     R- Los filtros de la segunda Conv (64) ya no ven los pixeles crudos, sino los mapas de la primera capa.
        Por eso detectan patrones mas compuestos como esquinas o texturas 
 
  3. Riesgo: si añades *muchas* capas Conv+Pool con pocas imágenes, ¿qué
     falla típico verías en las curvas train vs validation? ¿Qué harías
     primero para mitigarlo (Dropout, más datos, menos filtros…)? Elige
     *una* medida y justifica.
     R- 


5 Pregunta 4 — Formas: de volumen a vector
══════════════════════════════════════════

  Supón que, justo antes del Flatten, el tensor tiene forma `(7, 7, 64)'
  (lote omitido: una sola imagen).


5.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌

  1. ¿Cuántos números salen del Flatten? (un solo entero)
     R- 7x7x64 = 3136 numeros
  2. Si la siguiente Dense tiene *32 neuronas* (con bias), ¿cuántos
     parámetros tiene *esa* Dense?
     R- 3136 numeros x 32 neuronas + 32 da un total 100384 parametros.

  3. Si en vez de Flatten usas *Global Average Pooling* (un promedio por
     canal), ¿qué forma tendrías a la salida y cuántos valores serían?
     ¿Ventaja frente a Flatten cuando la imagen de entrada es más
     grande?


6 Pregunta 5 — Softmax y el error “casi seguro”
═══════════════════════════════════════════════

  Una CNN de 3 clases (inundación, incendio, tornado) saca logits que,
  tras softmax, dan:

  ┌────
  │   P = [0.10, 0.05, 0.85]
  └────

  La etiqueta verdadera (one-hot) es `[0, 1, 0]' (incendio).


6.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌

  1. ¿Qué clase predice el modelo (`argmax')?
  2. ¿Está “seguro” o “confundido”? Usa los números, no adjetivos
     vacíos.
  3. Sin calcular la fórmula exacta: argumenta si la *categorical
     crossentropy* de este ejemplo será *alta* o *baja*, y por qué
     (pista: castiga cuando la probabilidad de la clase correcta es
     pequeña).


7 Pregunta 6 — Padding, stride y “se me achicó la imagen”
═════════════════════════════════════════════════════════

  Entrada *32×32*, kernel *5×5*, *un* filtro, un canal.


7.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌

  Completa la tabla (escribe el alto×ancho de salida):

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   padding  stride  salida (alto×ancho) 
  ──────────────────────────────────────
   valid         1                      
   valid         2                      
   same          1                      
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  Luego: si encadenas *tres* MaxPool(2×2) seguidos sobre una imagen
  32×32 (sin cuidar bordes), ¿qué problema práctico aparece para
  clasificar objetos *pequeños* o detalles finos?


8 Pregunta 7 — Dropout: ¿dónde y para qué?
══════════════════════════════════════════

  En `CNNriesgo' hay `Dropout(0.5)' después del pooling y otra vez antes
  de la salida.


8.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌

  1. Durante *entrenamiento*, ¿qué hace Dropout(0.5) en una capa densa
     de 32 neuronas (en promedio cuántas “sobreviven” por paso)?
  2. Durante *inferencia* (`predict'), ¿se apagan neuronas al azar? ¿Por
     qué sí o no?
  3. Un compañero pone Dropout *solo* en la última época “para que no se
     sobreajuste al final”. ¿Tiene sentido? Critica la idea en 3–5
     líneas.


9 Pregunta 8 — Diseño: 5 clases de animales
═══════════════════════════════════════════

  Debes adaptar `CNNriesgo' a: ranas, arañas, monos, ballenas, pájaros.


9.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌

  1. ¿Cuántas neuronas debe tener la *última* Dense y qué activación?
     ¿Por qué?
  2. Si todas las fotos entran a *224×224×3* pero el modelo tiene
     `input_shape=(21,28,3)', ¿qué *debe* pasar antes del `fit'? (una
     frase operativa)
  3. Propón *una* mejora de arquitectura (segundo Conv, BatchNorm, data
     augmentation…)  y di *qué síntoma* en train/val te haría pensar que
     esa mejora era necesaria.


10 Pregunta 9 — CNN vs MLP vs RNN (mismo problema, mala herramienta)
════════════════════════════════════════════════════════════════════

  Tres escenarios. Elige *CNN*, *MLP* o *RNN/Transformer* y justifica en
  *una* frase cada uno:

  1. Predecir si un alumno aprueba con promedio, faltas y horas de
     estudio (tabla).
  2. Clasificar fotos de semáforo (rojo / amarillo / verde).
  3. Autocompletar la siguiente línea de código dado el prefijo escrito.

  Si aplastas la foto del semáforo y usas un MLP “grande”, ¿puede
  *aprender*? ¿Qué sacrificas respecto a una CNN? (parámetros, datos,
  invariancia…)


11 Pregunta 10 — Experimento mental: mover un gato
══════════════════════════════════════════════════

  Entrenaste una CNN que detecta “hay un gato” en fotos 64×64. En el
  test, el mismo gato aparece *corrido 10 píxeles a la derecha*, mismo
  fondo, misma escala.


11.0.1 Tareas
╌╌╌╌╌╌╌╌╌╌╌╌╌

  1. ¿Por qué una CNN tiene *más chance* de seguir acertando que un MLP
     que ve el vector aplastado? (pesos compartidos / detección local)
  2. Si en vez de correrlo lo *giraras 90°* y nunca viste gatos de lado
     en el train, ¿la CNN “mágica” garantiza acierto? ¿Qué haría falta
     (augmentation, más datos…)?
  3. Escribe *una* pregunta que tú le harías a un compañero para
     comprobar si entendió qué son los *pesos del kernel* (no copies las
     de arriba).


12 Autoevaluación rápida (opcional)
═══════════════════════════════════

  Marca 1–5 (1 = no entendí, 5 = lo explicaría en pizarrón):

  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
   Tema                                Nota 
  ──────────────────────────────────────────
   Producto punto del kernel =  4                
   Conteo de parámetros Conv vs Dense =  3      
   Efecto de apilar Conv+Pool  =         2             
   Softmax + pérdida  = 2                      
   Dropout train vs inferencia  = 2          
  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━


13 Notas al pie (fórmulas útiles — no sustituyen el razonamiento)
═════════════════════════════════════════════════════════════════

  • Salida convolución (un eje), padding valid: \(\lfloor (N - K)/S
    \rfloor + 1\)
  • Padding same + stride 1: salida ≈ mismo \(N\)
  • Parámetros Conv2D: \(K_h \cdot K_w \cdot C_{in} \cdot C_{out} +
    C_{out}\) (si hay bias)
  • Parámetros Dense: \(n_{in} \cdot n_{out} + n_{out}\) (si hay bias)
