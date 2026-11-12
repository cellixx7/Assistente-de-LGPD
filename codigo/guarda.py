# guarda.py
"""Guarda especialista: extrai fatos da pergunta, aplica regras em ordem de cautela e guarda o rastro."""
from texto import tokenizar

# Nota mínima de similaridade para considerar que existe documento relevante.
LIMIAR_SIMILARIDADE = 0.15


def conjunto(palavras):
    """Converte uma lista de palavras no conjunto de radicais usado nas comparações."""
    return set(tokenizar(" ".join(palavras)))


PALAVRAS_TEMA = conjunto([
    "lgpd", "dado", "pessoal", "privacidade", "consentimento", "titular",
    "anpd", "encarregado", "dpo", "incidente", "vazamento", "marketing",
    "sensível", "criança", "tratamento", "controlador", "operador",
    "segurança", "eliminação", "sanção", "proteção", "anonimização",
    "portabilidade",
])
PALAVRAS_INCIDENTE = conjunto([
    "vazamento", "vazou", "vazar", "incidente", "invasão", "invadiram",
    "invadido", "hackeado", "hacker", "ransomware", "roubaram", "ataque",
])
PALAVRAS_OCORRENCIA = conjunto([
    "ontem", "hoje", "agora", "aconteceu", "ocorreu", "sofremos", "sofri",
    "tivemos", "tive", "vazou", "invadiram", "hackeado", "roubaram",
    "descobri", "descobrimos", "fomos",
])
PALAVRAS_JURIDICO = conjunto([
    "advogado", "processar", "processado", "indenização", "indenizar",
    "demitir", "demissão", "justiça", "judicial", "liminar",
])

# Regras em ordem de cautela: "se" lista fatos verdadeiros, "nao" lista fatos falsos.
REGRAS = [
    {"id": "R1", "nome": "pergunta vazia ou sem palavras úteis",
     "se": ["pergunta_vazia"], "nao": [],
     "efeito": ("decisao", "recusar"),
     "motivo": "não há o que buscar na base"},
    {"id": "R2", "nome": "incidente em curso",
     "se": ["cita_incidente", "marca_ocorrencia"], "nao": [],
     "efeito": ("fato", "incidente_em_curso"),
     "motivo": "a pergunta cita um incidente e diz que ele aconteceu"},
    {"id": "R3", "nome": "encaminhar incidente",
     "se": ["incidente_em_curso"], "nao": [],
     "efeito": ("decisao", "encaminhar"),
     "motivo": "incidente real exige comunicação à ANPD, não resposta de FAQ",
     "destino": "encarregado da empresa e ANPD"},
    {"id": "R4", "nome": "aconselhamento jurídico",
     "se": ["pede_juridico"], "nao": [],
     "efeito": ("decisao", "encaminhar"),
     "motivo": "caso concreto exige análise de um profissional do direito",
     "destino": "advogado"},
    {"id": "R5", "nome": "fora do tema LGPD",
     "se": [], "nao": ["tema_lgpd"],
     "efeito": ("decisao", "recusar"),
     "motivo": "a pergunta não trata de proteção de dados"},
    {"id": "R6", "nome": "sem documento acima do limiar",
     "se": ["tema_lgpd"], "nao": ["documento_encontrado"],
     "efeito": ("decisao", "recusar"),
     "motivo": "não encontrei isso na base"},
    {"id": "R7", "nome": "responder com a base",
     "se": ["tema_lgpd", "documento_encontrado"], "nao": [],
     "efeito": ("decisao", "responder"),
     "motivo": "o tema é LGPD e há documento acima do limiar"},
]


def extrair_fatos(pergunta, texto_expandido, resultados_busca):
    """Transforma a pergunta, a rede e a busca em fatos verdadeiros ou falsos para as regras."""
    palavras = set(tokenizar(pergunta))
    palavras_expandidas = set(tokenizar(texto_expandido))
    melhor_nota = resultados_busca[0][1] if resultados_busca else 0.0
    return {
        "pergunta_vazia": not palavras,
        "cita_incidente": bool(palavras_expandidas & PALAVRAS_INCIDENTE),
        "marca_ocorrencia": bool(palavras & PALAVRAS_OCORRENCIA),
        "incidente_em_curso": False,
        "pede_juridico": bool(palavras & PALAVRAS_JURIDICO),
        "tema_lgpd": bool(palavras_expandidas & PALAVRAS_TEMA),
        "documento_encontrado": melhor_nota >= LIMIAR_SIMILARIDADE,
    }


def regra_dispara(regra, fatos):
    """Diz se todos os fatos de "se" são verdadeiros e todos os de "nao" são falsos."""
    return all(fatos[f] for f in regra["se"]) and not any(fatos[f] for f in regra["nao"])


def descrever_teste(regra, fatos):
    """Mostra os fatos que a regra testou, com seus valores, para o rastro."""
    partes = [f"{f}={fatos[f]}" for f in regra["se"]]
    partes += [f"{f}={fatos[f]} (precisa ser False)" for f in regra["nao"]]
    return ", ".join(partes)


def decidir(fatos):
    """Percorre as regras em ordem e devolve a decisão, o motivo e o rastro de cada teste."""
    fatos = dict(fatos)
    rastro = []
    for regra in REGRAS:
        disparou = regra_dispara(regra, fatos)
        situacao = "dispara" if disparou else "não dispara"
        rastro.append(
            f"{regra['id']} {regra['nome']} | {descrever_teste(regra, fatos)} | {situacao}"
        )
        if not disparou:
            continue
        tipo, valor = regra["efeito"]
        if tipo == "fato":
            fatos[valor] = True
            rastro.append(f"   deduziu {valor}=True")
            continue
        return {
            "decisao": valor,
            "regra": regra["id"],
            "motivo": regra["motivo"],
            "destino": regra.get("destino"),
            "rastro": rastro,
            "fatos": fatos,
        }
    return {
        "decisao": "recusar",
        "regra": None,
        "motivo": "nenhuma regra se aplicou",
        "destino": None,
        "rastro": rastro,
        "fatos": fatos,
    }
