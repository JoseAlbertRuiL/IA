# -*- coding: utf-8 -*-
"""
Corpus de noticias verdaderas y falsas sobre 3I/ATLAS, con NLTK.

Uso (desde la carpeta Noticias):
    python corpus_atlas.py

Genera:
    corpus/verdadera/*.txt     un archivo por noticia verdadera
    corpus/falsa/*.txt         un archivo por noticia falsa
    metadatos.json             id, tema, etiqueta, titulo, fuente, url, verificacion
Y muestra estadisticas con NLTK (tokens, vocabulario, frecuencias, palabras distintivas).
"""
import json
import os
import re
import sys

import nltk
from nltk.corpus import CategorizedPlaintextCorpusReader, stopwords

from datos_noticias import NOTICIAS

# La consola de Windows puede no ser UTF-8
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

AQUI = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.join(AQUI, "corpus")


def descargar_recursos():
    """Descarga los recursos de NLTK que se usan (solo si faltan)."""
    for recurso, ruta in [("stopwords", "corpora/stopwords"), ("punkt_tab", "tokenizers/punkt_tab")]:
        try:
            nltk.data.find(ruta)
        except LookupError:
            nltk.download(recurso, quiet=True)


def construir_corpus():
    """Escribe los .txt (titulo + texto) por etiqueta y el JSON de metadatos."""
    for etiqueta in ("verdadera", "falsa"):
        os.makedirs(os.path.join(RAIZ, etiqueta), exist_ok=True)
    for n in NOTICIAS:
        ruta = os.path.join(RAIZ, n["etiqueta"], f"{n['id']}.txt")
        with open(ruta, "w", encoding="utf-8") as f:
            f.write(n["titulo"] + ".\n" + n["texto"] + "\n")
    with open(os.path.join(AQUI, "metadatos.json"), "w", encoding="utf-8") as f:
        json.dump(NOTICIAS, f, ensure_ascii=False, indent=2)


def cargar_corpus():
    """Lector categorizado de NLTK: la categoria es la carpeta (verdadera / falsa)."""
    # NLTK >= 3.10 solo lee corpus dentro de rutas registradas en nltk.data.path
    if RAIZ not in nltk.data.path:
        nltk.data.path.append(RAIZ)
    return CategorizedPlaintextCorpusReader(
        RAIZ,
        r"(verdadera|falsa)/.*\.txt",
        cat_pattern=r"(verdadera|falsa)/.*",
        encoding="utf-8",
    )


def palabras_utiles(corpus, categoria):
    """Tokens en minusculas, solo alfabeticos, sin stopwords en espanol."""
    sw = set(stopwords.words("spanish"))
    return [
        w.lower()
        for w in corpus.words(categories=categoria)
        if re.fullmatch(r"[a-záéíóúñü]+", w.lower()) and w.lower() not in sw and len(w) > 2
    ]


def main():
    descargar_recursos()
    construir_corpus()
    corpus = cargar_corpus()

    print(f"Noticias en el corpus: {len(corpus.fileids())}")
    print(f"Categorias: {corpus.categories()}\n")

    frecs = {}
    for cat in corpus.categories():
        todas = corpus.words(categories=cat)
        utiles = palabras_utiles(corpus, cat)
        frecs[cat] = nltk.FreqDist(utiles)
        print(f"== {cat.upper()} ==")
        print(f"  documentos : {len(corpus.fileids(categories=cat))}")
        print(f"  tokens     : {len(todas)}")
        print(f"  vocabulario: {len(set(utiles))} palabras unicas (sin stopwords)")
        print("  top 10     :", ", ".join(f"{w}({c})" for w, c in frecs[cat].most_common(10)))
        print()

    # Palabras que aparecen solo (o mucho mas) en una categoria
    vocab_v, vocab_f = set(frecs["verdadera"]), set(frecs["falsa"])
    print("Palabras exclusivas de VERDADERAS (mas frecuentes):")
    print("  ", [w for w, _ in frecs["verdadera"].most_common() if w not in vocab_f][:12])
    print("Palabras exclusivas de FALSAS (mas frecuentes):")
    print("  ", [w for w, _ in frecs["falsa"].most_common() if w not in vocab_v][:12])

    tipos = [n.get("tipo", "noticia") for n in NOTICIAS]
    print(f"\nPor tipo: noticias={tipos.count('noticia')}  tuits={tipos.count('tuit')}")

    # Conteo por tema y etiqueta
    print("\nNoticias por tema:")
    temas = sorted({n["tema"] for n in NOTICIAS})
    for t in temas:
        v = sum(1 for n in NOTICIAS if n["tema"] == t and n["etiqueta"] == "verdadera")
        f = sum(1 for n in NOTICIAS if n["tema"] == t and n["etiqueta"] == "falsa")
        print(f"  {t:<22} verdaderas={v}  falsas={f}")


if __name__ == "__main__":
    main()
