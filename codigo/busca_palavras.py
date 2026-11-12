# busca_palavras.py
"""Busca por palavras em comum (estilo Aula 06) que alimenta a guarda até entrar a busca vetorial."""
import math
from pathlib import Path

from texto import tokenizar


def carregar_corpus(pasta):
    """Lê os arquivos dNN.txt da pasta e devolve um dicionário {id: texto}."""
    corpus = {}
    for caminho in sorted(Path(pasta).glob("d*.txt")):
        corpus[caminho.stem] = caminho.read_text(encoding="utf-8").strip()
    return corpus


def similaridade(palavras_pergunta, palavras_documento):
    """Calcula o cosseno entre dois conjuntos de palavras (0 sem nada em comum, 1 iguais)."""
    a = set(palavras_pergunta)
    b = set(palavras_documento)
    if not a or not b:
        return 0.0
    return len(a & b) / math.sqrt(len(a) * len(b))


def buscar(pergunta, corpus, k=3):
    """Devolve os k documentos mais parecidos como lista de (id, nota, palavras em comum)."""
    palavras_pergunta = set(tokenizar(pergunta))
    resultados = []
    for id_doc, texto in corpus.items():
        palavras_doc = set(tokenizar(texto))
        nota = similaridade(palavras_pergunta, palavras_doc)
        if nota > 0:
            comuns = sorted(palavras_pergunta & palavras_doc)
            resultados.append((id_doc, nota, comuns))
    resultados.sort(key=lambda item: (-item[1], item[0]))
    return resultados[:k]
