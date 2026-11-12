# rede_semantica.py
"""Rede semântica do domínio LGPD: triplas sinonimo_de e e_um, com propriedades herdadas."""
from texto import normalizar, radical, tokenizar

# Triplas (origem, relação, destino): sinonimo_de expande a pergunta e e_um classifica.
REDE = [
    ("autorização", "sinonimo_de", "consentimento"),
    ("vazamento", "sinonimo_de", "incidente"),
    ("dpo", "sinonimo_de", "encarregado"),
    ("promoção", "sinonimo_de", "marketing"),
    ("propaganda", "sinonimo_de", "marketing"),
    ("apagar", "sinonimo_de", "eliminação"),
    ("excluir", "sinonimo_de", "eliminação"),
    ("multa", "sinonimo_de", "sanção"),
    ("cpf", "e_um", "dado_pessoal"),
    ("telefone", "e_um", "dado_pessoal"),
    ("endereço", "e_um", "dado_pessoal"),
    ("email", "e_um", "dado_pessoal"),
    ("saúde", "e_um", "dado_sensivel"),
    ("biometria", "e_um", "dado_sensivel"),
    ("dado_sensivel", "e_um", "dado_pessoal"),
]

# Propriedades ficam nos nós de cima e são herdadas pelos nós de baixo.
PROPRIEDADES = {
    "dado_pessoal": {"pode_exibir": "nao"},
}


def chave(termo):
    """Converte um termo da rede no radical usado para comparar com a pergunta."""
    return radical(normalizar(termo))


def pai(no, rede):
    """Devolve o nó de cima pela relação e_um, ou None."""
    for origem, relacao, destino in rede:
        if relacao == "e_um" and chave(origem) == chave(no):
            return destino
    return None


def consultar(no, propriedade, rede, propriedades, mostrar=False):
    """Procura a propriedade no nó e, se não achar, sobe pela relação e_um."""
    caminho, atual = [], no
    while atual is not None:
        caminho.append(atual)
        if propriedade in propriedades.get(atual, {}):
            if mostrar:
                print("  caminho:", " -> ".join(caminho))
            return propriedades[atual][propriedade]
        atual = pai(atual, rede)
    if mostrar:
        print("  caminho:", " -> ".join(caminho), "(fim da rede)")
    return None


def expandir(palavras, rede):
    """Acrescenta os sinônimos da rede e devolve (palavras expandidas, acréscimos)."""
    expandidas = list(palavras)
    acrescimos = []
    for origem, relacao, destino in rede:
        if relacao != "sinonimo_de" or chave(origem) not in palavras:
            continue
        novas = [p for p in tokenizar(destino) if p not in expandidas]
        if novas:
            expandidas.extend(novas)
            acrescimos.append((origem, destino))
    return expandidas, acrescimos
