# Captura de rostros

Ejecuta desde la raiz del proyecto:

```powershell
python haar_cascade/haarcascade.py
```

El script conserva la estructura del ejemplo original. Al principio puedes editar:

- `persona = 'yo'`: carpeta de destino (yo, persona_2, persona_3, persona_4 o persona_5).
- `fuente = 0`: camara. Para un video usa una ruta, por ejemplo `fuente = r'C:\Videos\persona2.mp4'`.
- `cada = 1`: guarda en cada cuadro con una cara detectada. Usa `cada = 30` para muestrear videos cada 30 cuadros.

Crea las cinco carpetas en dataset, guarda recortes de 200 por 200 pixeles y se detiene a las 1000 imagenes. ESC permite salir antes y continuar despues sin sobrescribir capturas. Usa una sola persona por captura. Varia suavemente posicion y expresion.

El clasificador haarcascade_frontalface_alt.xml se busca junto al script. Si falta, se usa el mismo XML incluido con OpenCV, sin descargar archivos. Haar detecta caras; la etiqueta de la persona la defines tu en `persona`.

La version anterior con argumentos de consola se conserva en captura_avanzada.py.
