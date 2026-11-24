# texto.py
"""Funções de texto compartilhadas pela rede semântica, pela busca e pela guarda."""
import re
import unicodedata

# Palavras sem valor de busca (já sem acento), retiradas antes de comparar textos.
PALAVRAS_VAZIAS = {
    "a", "as", "o", "os", "um", "uma", "uns", "umas", "de", "do", "da", "dos",
    "das", "em", "no", "na", "nos", "nas", "por", "pelo", "pela", "pelos",
    "pelas", "para", "pra", "com", "sem", "sobre", "entre", "ate", "que", "e",
    "ou", "se", "ao", "aos", "como", "qual", "quais", "quando", "onde", "quem",
    "eu", "me", "voce", "vc", "meu", "minha", "meus", "minhas", "nosso", "nossa",
    "seu", "sua", "seus", "suas", "preciso", "posso", "pode", "podem", "devo",
    "deve", "ser", "sao", "foi", "tem", "ter", "ha", "mais", "muito", "isso",
    "esse", "essa", "este", "esta", "mas", "ja", "nao", "sim",
}


def normalizar(texto):
    """Põe o texto em minúsculas e remove os acentos."""
    decomposto = unicodedata.normalize("NFD", texto.lower())
    return "".join(c for c in decomposto if unicodedata.category(c) != "Mn")


def radical(palavra):
    """Reduz o plural simples ao singular (dados vira dado, titulares vira titular)."""
    if palavra.endswith(("oes", "aes")):
        return palavra[:-3] + "ao"
    if len(palavra) > 4 and palavra.endswith("ais"):
        return palavra[:-3] + "al"
    if len(palavra) > 4 and palavra.endswith("eis"):
        return palavra[:-3] + "el"
    if palavra.endswith("ns"):
        return palavra[:-2] + "m"
    if len(palavra) > 4 and palavra.endswith("res"):
        return palavra[:-2]
    if len(palavra) > 3 and palavra.endswith("s"):
        return palavra[:-1]
    return palavra


def tokenizar(texto, remover_vazias=True):
    """Divide o texto em radicais de palavras sem acentos, tirando as vazias se pedido."""
    palavras = re.findall(r"[a-z0-9]+", re.sub(r"(?<=\w)-(?=\w)", "", normalizar(texto)))
    if remover_vazias:
        palavras = [p for p in palavras if p not in PALAVRAS_VAZIAS]
    return [radical(p) for p in palavras if len(p) > 1]
