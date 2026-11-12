# assistente.py
"""Liga rede semântica, busca e guarda para decidir o que fazer com uma pergunta."""
from busca_palavras import buscar
from guarda import julgar, perceber
from rede_semantica import REDE, expandir
from texto import tokenizar


def tratar_pergunta(pergunta, corpus, usar_rede=True):
    """Executa rede, busca e guarda e devolve um dicionário com o resultado de cada etapa."""
    pergunta = pergunta or ""
    rede = REDE if usar_rede else []
    palavras = tokenizar(pergunta, remover_vazias=False)
    expandidas, acrescimos = expandir(palavras, rede)
    texto_expandido = " ".join([pergunta] + [destino for _, destino in acrescimos])
    documentos = buscar(texto_expandido, corpus)
    melhor_nota = documentos[0][1] if documentos else 0.0
    fatos = perceber(set(palavras), set(expandidas), melhor_nota, rede)
    resultado = julgar(fatos, set(palavras))
    resultado.update({
        "pergunta": pergunta,
        "acrescimos": acrescimos,
        "documentos": documentos,
    })
    return resultado
