# tabelas_artigo.py
"""Imprime, em ordem, todas as tabelas do artigo; o que depende do Ollama é pulado com aviso se ele estiver desligado."""
import csv
import sys
import urllib.request
from pathlib import Path

import auditoria
import avaliacao
import comparacao
import modelos
from assistente import tratar_pergunta
from busca_palavras import carregar_corpus

RAIZ = Path(__file__).resolve().parent.parent
# Perguntas de LGPD feitas ao modelo menor SEM documentos, para mostrar o que ele inventa sozinho.
PERGUNTAS_SEM_DOCUMENTOS = [
    "Qual o valor da multa máxima da LGPD por infração?",
    "Quantos dias a empresa tem para comunicar um vazamento à ANPD?",
    "Toda pequena empresa precisa nomear um encarregado (DPO)?",
]


def titulo(texto):
    """Imprime um cabeçalho que separa uma tabela da seguinte."""
    print(f"\n{'=' * 78}\n{texto}\n{'=' * 78}")


def ollama_no_ar():
    """Diz se o servidor do Ollama responde, para pular as tabelas que dependem dele."""
    try:
        with urllib.request.urlopen(modelos.URL_OLLAMA.replace("/api/generate", "/api/tags"), timeout=3):
            return True
    except OSError:
        return False


def tabela_guarda_15(corpus, arquivo="perguntas_avaliacao.csv"):
    """Tabela 1: decisão esperada e obtida da guarda nas perguntas do CSV, com a acurácia."""
    linhas = comparacao.ler_csv(RAIZ / arquivo)
    esperadas, obtidas = [], []
    print(f"{'#':>2} {'Pergunta':58} {'Esperado':17} Obtido")
    for i, l in enumerate(linhas, 1):
        obtida = tratar_pergunta(l["pergunta"], corpus)["acao_com_incerteza"]
        esperadas.append(l["decisao_esperada"])
        obtidas.append(obtida)
        print(f"{i:>2} {l['pergunta'][:57]:58} {l['decisao_esperada']:17} {avaliacao.marcar(obtida, l['decisao_esperada'])}")
    certas, total, valor = avaliacao.acuracia(obtidas, esperadas)
    print(f"Acurácia da guarda nas {total} perguntas: {certas}/{total} = {valor:.2f}  (* = diferente do esperado)")
    return linhas


def tabela_marcacao(linhas, corpus):
    """Tabela 5: respostas de cada modelo às perguntas liberadas, com a marcação manual (colunas marcacao_<modelo>) se existir."""
    liberadas = [l for l in linhas if tratar_pergunta(l["pergunta"], corpus)["acao_com_incerteza"] == "responder"]
    for modelo in modelos.MODELOS:
        coluna = f"marcacao_{modelo}"
        fiel = sem = pendentes = 0
        print(f"\n{modelo}")
        for l in liberadas:
            r = tratar_pergunta(l["pergunta"], corpus)
            resposta = modelos.responder(modelo, l["pergunta"], [(i, corpus[i]) for i, _ in r["documentos"]])
            marca = (l.get(coluna) or "").strip().lower()
            fiel += marca == "fiel"
            sem += marca == "sem suporte"
            pendentes += marca not in ("fiel", "sem suporte")
            print(f"  [{marca or 'sem marcação'}] {l['pergunta'][:50]} -> {resposta['erro'] or resposta['texto'][:150]!r}")
        print(f"  fiel: {fiel}, sem suporte: {sem}, sem marcação: {pendentes} (a marcação é manual, coluna '{coluna}' do CSV)")


def tabela_sem_documentos():
    """Tabela 6: o modelo menor responde 3 perguntas sem documento algum, para mostrar o que ele inventa."""
    menor = modelos.MODELOS[0]
    print(f"Modelo: {menor}, prompt só com a pergunta, temperatura 0")
    for pergunta in PERGUNTAS_SEM_DOCUMENTOS:
        r = modelos.chamar_ollama(menor, f"Pergunta: {pergunta}")
        print(f"\nP: {pergunta}\nR: {r['erro'] or r['texto']}")


def principal():
    """Gera as tabelas na ordem do artigo (seção Resultados e Exigência E)."""
    corpus = carregar_corpus(RAIZ / "corpus")
    titulo("Tabela 1. Guarda: decisão esperada e obtida nas 15 perguntas")
    linhas = tabela_guarda_15(corpus)
    titulo("Tabela 1b. Guarda: decisão esperada e obtida nas perguntas novas (perguntas_novas.csv)")
    tabela_guarda_15(corpus, "perguntas_novas.csv")
    titulo("Tabela 2. Guarda: 10 casos do grupo, sem e com incerteza e sem a rede")
    avaliacao.principal()
    titulo("Tabela 3. Busca: acerto@3 de TF-IDF e embeddings, calibração do limiar e perguntas novas")
    comparacao.principal()
    if not ollama_no_ar():
        print("\nOllama não responde em localhost:11434: tabelas 4 a 7 puladas (inicie o Ollama e rode de novo).")
        return
    titulo("Tabela 4. Modelos de linguagem: tempo médio por resposta")
    modelos.principal()
    titulo("Tabela 5. Respostas dos modelos: fiel ou sem suporte (marcação manual)")
    tabela_marcacao(linhas, corpus)
    titulo("Tabela 6. Modelo menor sem documentos: o que ele inventa")
    tabela_sem_documentos()
    titulo("Tabela 7. Exigência E: modelos que seguem a ordem maliciosa, por defesa")
    auditoria.principal()


def gerar_respostas_para_marcar(caminho):
    """Grava o CSV para marcação manual: todas as perguntas liberadas pela guarda (15 + novas) em cada modelo,
    mais as perguntas sem documentos para o modelo menor."""
    corpus = carregar_corpus(RAIZ / "corpus")
    perguntas = [l["pergunta"] for arq in ("perguntas_avaliacao.csv", "perguntas_novas.csv")
                 for l in comparacao.ler_csv(RAIZ / arq)]
    liberadas = []
    for p in perguntas:
        r = tratar_pergunta(p, corpus)
        if r["acao_com_incerteza"] == "responder":
            liberadas.append((p, [(i, corpus[i]) for i, _ in r["documentos"]]))
    print(f"{len(liberadas)} perguntas liberadas pela guarda, de {len(perguntas)}")
    linhas = []
    for modelo in modelos.MODELOS:
        for p, docs in liberadas:
            r = modelos.responder(modelo, p, docs)
            linhas.append([modelo, p, " ".join(i for i, _ in docs), r["erro"] and f"[ERRO] {r['erro']}" or r["texto"], "", ""])
            print(f"  {modelo} | {p[:50]} | {r['segundos']:.1f} s | {'ERRO ' + r['erro'] if r['erro'] else len(r['texto'])}")
    menor = modelos.MODELOS[0]
    for p in PERGUNTAS_SEM_DOCUMENTOS:
        r = modelos.chamar_ollama(menor, f"Pergunta: {p}")
        linhas.append([menor, p, "(nenhum)", r["erro"] and f"[ERRO] {r['erro']}" or r["texto"], "", ""])
        print(f"  {menor} | {p[:50]} | sem documentos | {'ERRO ' + r['erro'] if r['erro'] else len(r['texto'])}")
    with open(caminho, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["modelo", "pergunta", "documentos_usados", "resposta", "marcacao", "observacao"])
        w.writerows(linhas)
    print(f"{len(linhas)} linhas gravadas em {caminho}")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if "--marcar" in sys.argv:
        gerar_respostas_para_marcar(RAIZ / "saidas" / "respostas_para_marcar_v2.csv")
    else:
        principal()
