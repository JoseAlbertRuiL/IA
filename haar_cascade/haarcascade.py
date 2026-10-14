from pathlib import Path
import cv2 as cv


persona = 'persona_5'  # yo, persona_2, persona_3, persona_4, persona_5
fuente = r'C:\Users\jarlj\Downloads\8724367-uhd_4096_2160_25fps.mp4'  # 0 = camara; para video: r'C:\Videos\persona2.mp4'
cada = 1  # Camara rapida: 1; para tomar cada 30 cuadros: 30

base = Path(__file__).resolve().parent
for nombre in ('yo', 'persona_2', 'persona_3', 'persona_4', 'persona_5'):
    (base / 'dataset' / nombre).mkdir(parents=True, exist_ok=True)
carpeta = base / 'dataset' / persona
carpeta.mkdir(parents=True, exist_ok=True)



xml = base / 'haarcascade_frontalface_alt.xml'
if not xml.is_file():
    xml = Path(cv.data.haarcascades) / 'haarcascade_frontalface_alt.xml'
rostro = cv.CascadeClassifier(str(xml))
if rostro.empty():
    raise RuntimeError(f'No se pudo cargar el clasificador: {xml}')
if cada < 1:
    raise ValueError('cada debe ser mayor que cero')

existentes = list(carpeta.glob('cara_*.jpg'))
count = len(existentes)
numero = max((int(p.stem.split('_')[-1]) for p in existentes), default=0)
cuadro = 0
cap = cv.VideoCapture(fuente)
try:
    if not cap.isOpened():
        raise RuntimeError('No se pudo abrir la camara o el video')
    while count < 1000:
        ret, frame = cap.read()
        if not ret:
            break
        # Reducir videos grandes antes de detectar y mostrar, manteniendo proporciones.
        alto, ancho = frame.shape[:2]
        escala = min(1.0, 720 / max(alto, ancho))
        if escala < 1:
            frame = cv.resize(frame, (round(ancho * escala), round(alto * escala)),
                              interpolation=cv.INTER_AREA)
        cuadro += 1
        if cuadro % cada == 0:
            gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
            rostros = rostro.detectMultiScale(gray, 1.3, 5)
            if len(rostros) == 1:
                for x, y, w, h in rostros:
                    # Recortar antes de dibujar para guardar la cara sin rectangulo.
                    img = cv.resize(frame[y:y+h, x:x+w], (200, 200))
                    name = carpeta / f'cara_{numero + 1:04d}.jpg'
                    if not cv.imwrite(str(name), img):
                        raise RuntimeError(f'No se pudo guardar: {name}')
                    numero += 1
                    count += 1
                    cv.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv.imshow('cara', img)
        cv.putText(frame, f'{persona}: {count}/1000', (10, 30),
                   cv.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv.imshow('rostros', frame)
        k = cv.waitKey(1)
        if k == 27:
            break
finally:
    cap.release()
    cv.destroyAllWindows()
    print(f'{count}/1000 imagenes guardadas en {carpeta}')
