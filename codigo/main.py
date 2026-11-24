# main.py
"""Executa o assistente de LGPD: uma pergunta da linha de comando ou a demonstração completa."""
import sys
from pathlib import Path

from assistente import tratar_pergunta
from busca_palavras import carregar_corpus
from casos_teste import CASOS

PASTA_CORPUS = Path(__file__).resolve().parent.parent / "corpus"


def imprimir_resultado(resultado, corpus):
    """Imprime pergunta, rede, busca, fatos, ciclos do motor, explicação e decisão."""
    print(f"\nPergunta: {resultado['pergunta']!r}")
    if resultado["acrescimos"]:
        for origem, destino in resultado["acrescimos"]:
            print(f"  Rede semântica: {origem} -> {destino} (sinonimo_de)")
    else:
        print("  Rede semântica: nenhum sinônimo acrescentado")
    if resultado["documentos"]:
        for id_doc, nota in resultado["documentos"]:
            print(f"  Busca: {id_doc} nota={nota:.3f}")
    else:
        print("  Busca: nenhum documento encontrado")
    print("  Fatos percebidos:", resultado["fatos"])
    for linha in resultado["ciclos"]:
        print(f"  {linha}")
    print("  Explicação:")
    for linha in resultado["explicacao"]:
        print(f"    {linha}")
    print("  Confianças:", resultado["confianca"])
    print(
        f"  Decisão: {resultado['acao_com_incerteza'].upper()} "
        f"(sem incerteza seria {resultado['acao_sem_incerteza']})"
    )
    if resultado["acao_com_incerteza"] == "responder":
        id_doc = resultado["documentos"][0][0]
        print(f"  Documento que iria ao modelo: [{id_doc}] {corpus[id_doc]}")


def principal():
    """Roda a pergunta passada na linha de comando ou, sem argumentos, os 10 casos e uma pergunta vazia."""
    corpus = carregar_corpus(PASTA_CORPUS)
    print(f"Corpus carregado: {len(corpus)} documentos")
    if len(sys.argv) > 1:
        perguntas = [" ".join(sys.argv[1:])]
    else:
        perguntas = [pergunta for pergunta, _ in CASOS] + [""]
    for pergunta in perguntas:
        imprimir_resultado(tratar_pergunta(pergunta, corpus), corpus)


if __name__ == "__main__":
    principal()
