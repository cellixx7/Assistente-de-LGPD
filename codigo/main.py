# main.py
"""Executa o assistente de LGPD: uma pergunta da linha de comando ou a demonstração completa."""
import sys
from pathlib import Path

from assistente import tratar_pergunta
from busca_palavras import carregar_corpus

PASTA_CORPUS = Path(__file__).resolve().parent.parent / "corpus"

PERGUNTAS_DEMO = [
    "Preciso de autorização para mandar promoção por WhatsApp?",
    "Qual o prazo para responder o titular que pede acesso aos dados?",
    "Pequena empresa precisa de DPO?",
    "O que é um vazamento de dados?",
    "Tivemos um vazamento de dados hoje, o que faço?",
    "Posso demitir um funcionário que pediu seus dados? Preciso de advogado?",
    "Qual a receita de bolo de cenoura?",
    "",
]


def imprimir_resultado(resultado, corpus):
    """Imprime a pergunta, a rede, a busca, o rastro das regras e a decisão."""
    print(f"\nPergunta: {resultado['pergunta']!r}")
    if resultado["acrescimos"]:
        for termo, relacao, novo in resultado["acrescimos"]:
            print(f"  Rede semântica: {termo} -> {novo} ({relacao})")
    else:
        print("  Rede semântica: nenhum termo acrescentado")
    if resultado["documentos"]:
        for id_doc, nota, comuns in resultado["documentos"]:
            print(f"  Busca: {id_doc} nota={nota:.3f} palavras={', '.join(comuns)}")
    else:
        print("  Busca: nenhum documento com palavras em comum")
    print("  Rastro da guarda:")
    for linha in resultado["rastro"]:
        print(f"    {linha}")
    destino = f" para {resultado['destino']}" if resultado["destino"] else ""
    print(
        f"  Decisão: {resultado['decisao'].upper()}{destino} "
        f"(regra {resultado['regra']}: {resultado['motivo']})"
    )
    if resultado["decisao"] == "responder":
        id_doc = resultado["documentos"][0][0]
        print(f"  Documento que iria ao modelo: [{id_doc}] {corpus[id_doc]}")


def principal():
    """Roda a pergunta passada na linha de comando ou, sem argumentos, a demonstração."""
    corpus = carregar_corpus(PASTA_CORPUS)
    print(f"Corpus carregado: {len(corpus)} documentos")
    if len(sys.argv) > 1:
        perguntas = [" ".join(sys.argv[1:])]
    else:
        perguntas = PERGUNTAS_DEMO
    for pergunta in perguntas:
        imprimir_resultado(tratar_pergunta(pergunta, corpus), corpus)


if __name__ == "__main__":
    principal()
