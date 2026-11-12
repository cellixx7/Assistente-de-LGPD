# assistente.py
"""Liga rede semântica, busca e guarda para decidir o que fazer com uma pergunta."""
from busca_palavras import buscar
from guarda import decidir, extrair_fatos
from rede_semantica import expandir_pergunta


def tratar_pergunta(pergunta, corpus):
    """Executa rede, busca e guarda e devolve um dicionário com o resultado de cada etapa."""
    pergunta = pergunta or ""
    texto_expandido, acrescimos = expandir_pergunta(pergunta)
    documentos = buscar(texto_expandido, corpus)
    fatos = extrair_fatos(pergunta, texto_expandido, documentos)
    resultado = decidir(fatos)
    resultado.update({
        "pergunta": pergunta,
        "texto_expandido": texto_expandido,
        "acrescimos": acrescimos,
        "documentos": documentos,
    })
    return resultado
