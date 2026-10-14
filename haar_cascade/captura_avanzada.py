"""Captura rostros: cada 3 cuadros de camara o cada 30 de video."""
import argparse
import hashlib
from pathlib import Path

import cv2 as cv

BASE = Path(__file__).resolve().parent
PERSONAS = ('yo', 'persona_2', 'persona_3', 'persona_4', 'persona_5')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--persona', choices=PERSONAS, default='yo')
    parser.add_argument('--videos', nargs='+', type=Path)
    parser.add_argument('--camara', type=int, default=0)
    parser.add_argument('--cada', type=int, help='Guardar cada N cuadros (camara: 3; video: 30)')
    parser.add_argument('--sin-ventana', action='store_true')
    parser.add_argument('--preparar', action='store_true', help='Solo crea las cinco carpetas')
    args = parser.parse_args()
    if args.cada is not None and args.cada < 1:
        parser.error('--cada debe ser un entero mayor que cero.')
    intervalo = args.cada if args.cada is not None else (30 if args.videos else 3)
    for persona in PERSONAS:
        (BASE / 'dataset' / persona).mkdir(parents=True, exist_ok=True)
    if args.preparar:
        return
    detector = cv.CascadeClassifier(str(BASE / 'haarcascade_frontalface_alt.xml'))
    if detector.empty():
        parser.error('No se pudo cargar el XML de Haar.')
    if args.videos and any(not p.is_file() for p in args.videos):
        parser.error('Todos los videos deben existir como archivos locales.')
    carpeta = BASE / 'dataset' / args.persona
    existentes = list(carpeta.glob('cara_*.jpg'))
    total = len(existentes)
    hashes = {hashlib.sha256(p.read_bytes()).digest() for p in existentes}
    indice = max((int(p.stem.split('_')[-1]) for p in existentes), default=0)
    detener = False
    try:
        for fuente in args.videos or [args.camara]:
            if total >= 1000 or detener:
                break
            cap = cv.VideoCapture(str(fuente) if isinstance(fuente, Path) else fuente)
            try:
                if not cap.isOpened():
                    raise RuntimeError(f'No se pudo abrir: {fuente}')
                cuadro = 0
                while total < 1000:
                    ok, frame = cap.read()
                    if not ok:
                        break
                    cuadro += 1
                    if cuadro % intervalo == 0:
                        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
                        caras = detector.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))
                        # No elegir automáticamente entre varias personas.
                        if len(caras) == 1:
                            x, y, w, h = caras[0]
                            cara = cv.resize(gray[y:y+h, x:x+w], (200, 200))
                            ok, encoded = cv.imencode('.jpg', cara)
                            if not ok:
                                raise RuntimeError('No se pudo codificar el rostro.')
                            datos = encoded.tobytes()
                            huella = hashlib.sha256(datos).digest()
                            if huella not in hashes:
                                indice += 1
                                destino = carpeta / f'cara_{indice:04d}.jpg'
                                with destino.open('xb') as archivo:
                                    archivo.write(datos)
                                hashes.add(huella)
                                total += 1
                                if total % 50 == 0:
                                    print(f'{args.persona}: {total}/1000', flush=True)
                    if not args.sin_ventana:
                        cv.putText(frame, f'{args.persona}: {total}/1000 | ESC: salir',
                                   (10, 30), cv.FONT_HERSHEY_SIMPLEX, .65, (0, 255, 0), 2)
                        cv.imshow('Captura de rostros', frame)
                        if cv.waitKey(1) & 0xFF == 27:
                            detener = True
                            break
            finally:
                cap.release()
    finally:
        cv.destroyAllWindows()
        print(f'{args.persona}: {total}/1000 imagenes en {carpeta}')
        if total < 1000:
            print(f'Faltan {1000-total}. Puedes continuar con otra captura o video de la misma persona.')


if __name__ == '__main__':
    main()
