# rede_semantica.py
"""Rede semântica do domínio LGPD: sinônimos e herança que expandem a pergunta do usuário."""
from texto import normalizar, radical, tokenizar

# Cada relação é (termo, tipo, termo relacionado); "e_um" sobe na herança.
RELACOES = [
    ("autorização", "sinonimo", "consentimento"),
    ("vazamento", "sinonimo", "incidente"),
    ("dpo", "sinonimo", "encarregado"),
    ("promoção", "sinonimo", "marketing"),
    ("propaganda", "sinonimo", "marketing"),
    ("apagar", "sinonimo", "eliminação"),
    ("excluir", "sinonimo", "eliminação"),
    ("multa", "sinonimo", "sanção"),
    ("cliente", "e_um", "titular"),
    ("funcionário", "e_um", "titular"),
    ("saúde", "e_um", "dado sensível"),
    ("biometria", "e_um", "dado sensível"),
    ("dado sensível", "e_um", "dado pessoal"),
]


def chave(termo):
    """Converte um termo de uma palavra no radical usado para comparar com a pergunta."""
    return radical(normalizar(termo))


def ancestrais(termo):
    """Sobe a herança (e_um) a partir do termo e devolve todos os ancestrais em ordem."""
    resultado = []
    atual = normalizar(termo)
    while True:
        pai = next(
            (b for a, rel, b in RELACOES if rel == "e_um" and normalizar(a) == atual),
            None,
        )
        if pai is None or pai in resultado:
            break
        resultado.append(pai)
        atual = normalizar(pai)
    return resultado


def expandir_pergunta(pergunta):
    """Acrescenta à pergunta os termos relacionados e devolve (texto expandido, acréscimos)."""
    palavras = set(tokenizar(pergunta))
    acrescimos = []
    for origem, relacao, destino in RELACOES:
        if relacao == "sinonimo":
            pares = [(origem, [destino]), (destino, [origem])]
        else:
            pares = [(origem, ancestrais(origem))]
        for termo, novos in pares:
            if chave(termo) not in palavras:
                continue
            for novo in novos:
                if set(tokenizar(novo)) <= palavras:
                    continue
                acrescimos.append((termo, relacao, novo))
    novos_termos = []
    for _, _, novo in acrescimos:
        if novo not in novos_termos:
            novos_termos.append(novo)
    texto_expandido = " ".join([pergunta] + novos_termos).strip()
    return texto_expandido, acrescimos
