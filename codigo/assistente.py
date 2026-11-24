# assistente.py
"""Liga rede semântica, busca e guarda para decidir o que fazer com uma pergunta."""
from busca_vetorial import BuscaEmbeddings
from guarda import julgar, perceber
from rede_semantica import REDE, expandir
from texto import tokenizar


_INDICES = {}


def indice_de(corpus):
    """Devolve o índice de embeddings do corpus, calculado uma vez só (carregar o modelo é lento)."""
    chave_corpus = tuple(corpus.items())
    if chave_corpus not in _INDICES:
        _INDICES[chave_corpus] = BuscaEmbeddings(corpus)
    return _INDICES[chave_corpus]


def tratar_pergunta(pergunta, corpus, usar_rede=True, busca=None):
    """Executa rede, busca e guarda e devolve um dicionário com o resultado de cada etapa."""
    pergunta = pergunta or ""
    rede = REDE if usar_rede else []
    palavras = tokenizar(pergunta, remover_vazias=False)
    expandidas, acrescimos = expandir(palavras, rede)
    texto_expandido = " ".join([pergunta] + [destino for _, destino in acrescimos])
    documentos = (busca or indice_de(corpus)).buscar(texto_expandido)
    melhor_nota = documentos[0][1] if documentos else 0.0
    fatos = perceber(set(palavras), set(expandidas), melhor_nota, rede)
    resultado = julgar(fatos, set(palavras))
    resultado.update({
        "pergunta": pergunta,
        "acrescimos": acrescimos,
        "documentos": documentos,
    })
    return resultado
