# avaliacao.py
"""Avalia a guarda nos 10 casos, sem e com incerteza, e mostra rastro, explicação e efeito da rede."""
from pathlib import Path

from assistente import tratar_pergunta
from busca_palavras import carregar_corpus
from casos_teste import CASOS
from guarda import LIMIAR_BUSCA, LIMIAR_CONFIANCA, REGRAS, verificar_base
from rede_semantica import REDE

PASTA_CORPUS = Path(__file__).resolve().parent.parent / "corpus"


def acuracia(decisoes, esperadas):
    """Calcula decisões certas dividido pelo total de casos."""
    certas = sum(d == e for d, e in zip(decisoes, esperadas))
    return certas, len(esperadas), certas / len(esperadas)


def marcar(valor, esperado):
    """Acrescenta um asterisco à decisão quando ela difere da esperada."""
    return valor + (" " if valor == esperado else "*")


def imprimir_tabela(linhas):
    """Imprime pergunta, decisão esperada e decisão obtida em cada modo, marcando os erros."""
    print(f"{'#':>2} {'Pergunta':46} {'Esperado':18} {'Sem incerteza':18} {'Com incerteza':18} Sem rede")
    for i, (pergunta, esperado, sem, com, sem_rede) in enumerate(linhas, 1):
        print(
            f"{i:>2} {pergunta[:45]:46} {esperado:18} {marcar(sem, esperado):18} "
            f"{marcar(com, esperado):18} {marcar(sem_rede, esperado)}"
        )
    print("(* = diferente do esperado)")


def principal():
    """Roda os 10 casos nos três modos e imprime acurácias, explicação e dependência da rede."""
    corpus = carregar_corpus(PASTA_CORPUS)
    resultados = []
    for pergunta, esperado in CASOS:
        completo = tratar_pergunta(pergunta, corpus)
        sem_rede = tratar_pergunta(pergunta, corpus, usar_rede=False)
        resultados.append((pergunta, esperado, completo, sem_rede))

    esperadas = [r[1] for r in resultados]
    sem = [r[2]["acao_sem_incerteza"] for r in resultados]
    com = [r[2]["acao_com_incerteza"] for r in resultados]
    sem_rede = [r[3]["acao_com_incerteza"] for r in resultados]

    print(f"Base: {len(REDE)} relações na rede, {len(REGRAS)} regras, "
          f"limiar da busca {LIMIAR_BUSCA}, limiar de confiança {LIMIAR_CONFIANCA}")
    print("Regras mortas (condição que ninguém produz):", verificar_base(REGRAS) or "nenhuma")
    print()
    imprimir_tabela([(p, e, s, c, r) for (p, e, _, _), s, c, r in zip(resultados, sem, com, sem_rede)])
    for nome, decisoes in [("sem incerteza", sem), ("com incerteza", com), ("com incerteza e sem a rede", sem_rede)]:
        certas, total, valor = acuracia(decisoes, esperadas)
        print(f"Acurácia {nome}: {certas}/{total} = {valor:.1f}")

    print("\nCasos que dependem da rede (certos com ela, errados sem ela):")
    for pergunta, esperado, completo, sr in resultados:
        if completo["acao_com_incerteza"] == esperado and sr["acao_com_incerteza"] != esperado:
            print(f"  {pergunta!r}: sem a rede decidiria {sr['acao_com_incerteza']}")

    print("\nCasos que a incerteza mudou:")
    for pergunta, esperado, completo, _ in resultados:
        if completo["acao_sem_incerteza"] != completo["acao_com_incerteza"]:
            print(f"  {pergunta!r}: {completo['acao_sem_incerteza']} -> {completo['acao_com_incerteza']} "
                  f"(confiança {completo['confianca'].get(completo['acao_sem_incerteza'])})")

    destaque = next(r for r in resultados if r[0].startswith("Tivemos um vazamento"))[2]
    print(f"\nRastro e explicação de um caso: {destaque['pergunta']!r}")
    print("  fatos percebidos:", destaque["fatos"])
    for linha in destaque["ciclos"]:
        print("  " + linha)
    for linha in destaque["explicacao"]:
        print("  " + linha)


if __name__ == "__main__":
    principal()
