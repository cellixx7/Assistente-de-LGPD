# comparacao.py
"""Mede o acerto@3 da busca TF-IDF e da busca por embeddings no CSV e recalibra o limiar da guarda."""
import csv
from pathlib import Path

from assistente import tratar_pergunta
from busca_palavras import carregar_corpus
from busca_vetorial import BuscaEmbeddings, BuscaTfidf
from casos_teste import CASOS
from guarda import LIMIAR_BUSCA

RAIZ = Path(__file__).resolve().parent.parent


def ler_csv(caminho):
    with open(caminho, encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def faixa_do_limiar(notas_com_resposta, notas_sem_resposta):
    """Devolve (maior nota sem resposta, menor nota com resposta, ponto médio da folga)."""
    teto, piso = max(notas_sem_resposta), min(notas_com_resposta)
    return teto, piso, (teto + piso) / 2


def principal():
    corpus = carregar_corpus(RAIZ / "corpus")
    linhas = ler_csv(RAIZ / "perguntas_avaliacao.csv")
    com_gabarito = [l for l in linhas if l["documento_correto"]]
    buscas = {"TF-IDF": BuscaTfidf(corpus), "Embeddings": BuscaEmbeddings(corpus)}

    print(f"Acerto@3 em {len(com_gabarito)} perguntas com documento correto (cosseno, top 3)\n")
    print(f"{'Pergunta':58} {'Correto':8} {'TF-IDF top 3':22} {'Embeddings top 3':22}")
    acertos = {nome: 0 for nome in buscas}
    for l in com_gabarito:
        celulas = []
        for nome, busca in buscas.items():
            ids = [i for i, _ in busca.buscar(l["pergunta"])]
            ok = l["documento_correto"] in ids
            acertos[nome] += ok
            celulas.append(f"{'OK ' if ok else 'ERRO'} {','.join(ids)}")
        print(f"{l['pergunta'][:57]:58} {l['documento_correto']:8} {celulas[0]:22} {celulas[1]:22}")
    print(f"\n{'Busca':12} {'Acerto@3':>9}")
    for nome, n in acertos.items():
        print(f"{nome:12} {n}/{len(com_gabarito)} = {n / len(com_gabarito):.2f}")

    # Calibração: a guarda vê a melhor nota dos embeddings sobre a pergunta já expandida pela rede.
    fora_dominio = ler_csv(RAIZ / "perguntas_fora_dominio.csv")  # só para calibrar; não entra no acerto@3 nem nas 15
    perguntas = {l["pergunta"]: l["decisao_esperada"] for l in linhas + fora_dominio} | dict(CASOS)
    com_resposta, sem_resposta = [], []
    for pergunta, esperado in perguntas.items():
        r = tratar_pergunta(pergunta, corpus, busca=buscas["Embeddings"])
        nota = r["documentos"][0][1]
        if esperado == "responder":
            com_resposta.append(nota)
        elif "sem_termo_do_dominio" in r["fatos"]:
            sem_resposta.append(nota)
    teto, piso, medio = faixa_do_limiar(com_resposta, sem_resposta)
    print(f"\nCalibração do limiar da busca (nota de embeddings, {len(perguntas)} perguntas únicas)")
    print(f"  maior nota fora do domínio ({len(sem_resposta)} perguntas): {teto:.3f}")
    print(f"  menor nota de pergunta a responder ({len(com_resposta)} perguntas): {piso:.3f}")
    print(f"  ponto médio da folga: {medio:.3f}; limiar atual no código: {LIMIAR_BUSCA}")
    if teto >= piso:
        acima = sum(n > LIMIAR_BUSCA for n in sem_resposta)
        print(f"  sem folga: as faixas se sobrepõem; com o limiar atual, {acima} de {len(sem_resposta)} perguntas fora do domínio "
              f"ainda acham documento, e só a regra R7 (recusar vence responder) as barra")


if __name__ == "__main__":
    principal()
