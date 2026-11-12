# guarda.py
"""Guarda especialista (Aula 06) no domínio LGPD: sensores, regras, motor de inferência e incerteza."""
from rede_semantica import PROPRIEDADES, REDE, chave, consultar
from texto import tokenizar

# Nota mínima de similaridade para o fato documento_encontrado.
LIMIAR_BUSCA = 0.15
# Confiança mínima para a guarda agir sozinha; abaixo disso, um humano decide.
LIMIAR_CONFIANCA = 0.7
# Ordem de cautela: recusar vence encaminhar_humano, que vence responder.
PRIORIDADE = ["recusar", "encaminhar_humano", "responder"]


def conjunto(palavras):
    """Converte uma lista de palavras no conjunto de radicais, mantendo gatilhos como "qual"."""
    return set(tokenizar(" ".join(palavras), remover_vazias=False))


VOCABULARIO_TEMA = conjunto([
    "lgpd", "dado", "pessoal", "privacidade", "consentimento", "titular",
    "anpd", "encarregado", "dpo", "incidente", "marketing", "sensível",
    "criança", "tratamento", "controlador", "operador", "segurança",
    "eliminação", "sanção", "proteção", "anonimização", "portabilidade",
])
GATILHOS_EXIBICAO = conjunto([
    "passa", "passar", "mostra", "mostrar", "manda", "mandar", "envia",
    "enviar", "informa", "fornece", "fornecer", "lista", "listar", "divulga",
    "divulgar", "qual",
])
GATILHOS_FRACOS = conjunto(["qual"])
GATILHOS_INCIDENTE = conjunto([
    "incidente", "invasão", "invadiram", "invadido", "hackeado", "hacker",
    "ransomware", "roubaram", "ataque", "vazou", "vazar",
])
GATILHOS_OCORRENCIA = conjunto([
    "ontem", "hoje", "agora", "aconteceu", "ocorreu", "sofremos", "sofri",
    "tivemos", "tive", "vazou", "invadiram", "hackeado", "roubaram",
    "descobri", "descobrimos", "fomos",
])
GATILHOS_JURIDICOS = conjunto([
    "advogado", "processar", "processado", "indenização", "indenizar",
    "demitir", "demissão", "justiça", "judicial", "liminar",
])

# Regras de produção SE condições ENTÃO conclusão; algumas concluem fatos intermediários.
REGRAS = [
    {"nome": "R1", "se": ["menciona_dado_pessoal", "pede_exibicao"], "entao": "vazamento_de_dado"},
    {"nome": "R2", "se": ["vazamento_de_dado"], "entao": "recusar"},
    {"nome": "R3", "se": ["cita_incidente", "marca_ocorrencia"], "entao": "incidente_em_curso"},
    {"nome": "R4", "se": ["incidente_em_curso"], "entao": "encaminhar_humano"},
    {"nome": "R5", "se": ["pede_orientacao_juridica"], "entao": "encaminhar_humano"},
    {"nome": "R6", "se": ["sem_termo_do_dominio"], "entao": "fora_do_dominio"},
    {"nome": "R7", "se": ["fora_do_dominio"], "entao": "recusar"},
    {"nome": "R8", "se": ["documento_encontrado"], "entao": "responder"},
]

# Fatos que os sensores (função perceber) sabem produzir.
FATOS_DOS_SENSORES = {
    "menciona_dado_pessoal", "pede_exibicao", "cita_incidente", "marca_ocorrencia",
    "pede_orientacao_juridica", "sem_termo_do_dominio", "documento_encontrado",
}


def vocabulario(rede):
    """Devolve o vocabulário do domínio: a lista do grupo mais os termos classificados na rede."""
    return VOCABULARIO_TEMA | {chave(o) for o, relacao, _ in rede if relacao == "e_um"}


def perceber(palavras, expandidas, melhor_nota, rede=REDE):
    """Transforma a pergunta, a expansão da rede e a nota da busca em um conjunto de fatos."""
    fatos = set()
    if any(consultar(p, "pode_exibir", rede, PROPRIEDADES) == "nao" for p in palavras):
        fatos.add("menciona_dado_pessoal")
    if palavras & GATILHOS_EXIBICAO:
        fatos.add("pede_exibicao")
    if expandidas & GATILHOS_INCIDENTE:
        fatos.add("cita_incidente")
    if palavras & GATILHOS_OCORRENCIA:
        fatos.add("marca_ocorrencia")
    if palavras & GATILHOS_JURIDICOS:
        fatos.add("pede_orientacao_juridica")
    if not expandidas & vocabulario(rede):
        fatos.add("sem_termo_do_dominio")
    if melhor_nota >= LIMIAR_BUSCA:
        fatos.add("documento_encontrado")
    return fatos


def encadear_para_frente(fatos, regras):
    """Dispara regras até não surgir fato novo e devolve (fatos finais, regras disparadas, ciclos)."""
    fatos, rastro, ciclos, ciclo = set(fatos), [], [], 0
    while True:
        ciclo += 1
        prontas = [r for r in regras if all(c in fatos for c in r["se"]) and r["entao"] not in fatos]
        if not prontas:
            ciclos.append(f"ciclo {ciclo}: nenhuma regra nova, fim")
            return fatos, rastro, ciclos
        regra = prontas[0]
        fatos.add(regra["entao"])
        rastro.append(regra["nome"])
        ciclos.append(
            f"ciclo {ciclo}: prontas {[r['nome'] for r in prontas]} "
            f"-> dispara {regra['nome']} -> novo fato {regra['entao']}"
        )


def decidir(fatos):
    """Escolhe a ação mais cautelosa entre as concluídas; sem ação, um humano decide."""
    for acao in PRIORIDADE:
        if acao in fatos:
            return acao
    return "encaminhar_humano"


def perceber_com_confianca(fatos, palavras):
    """Dá confiança 1,0 aos fatos, ou 0,5 ao pedido de exibição que veio só de gatilho fraco."""
    confianca = {fato: 1.0 for fato in fatos}
    if "pede_exibicao" in confianca and not palavras & (GATILHOS_EXIBICAO - GATILHOS_FRACOS):
        confianca["pede_exibicao"] = 0.5
    return confianca


def encadear_com_confianca(confianca, regras):
    """Encadeia para frente; cada conclusão recebe a menor confiança de suas condições."""
    confianca, mudou = dict(confianca), True
    while mudou:
        mudou = False
        for r in regras:
            if all(c in confianca for c in r["se"]) and r["entao"] not in confianca:
                confianca[r["entao"]] = min(confianca[c] for c in r["se"])
                mudou = True
    return confianca


def explicar(rastro, regras, acao):
    """Monta a explicação da decisão a partir das regras que dispararam."""
    linhas = []
    for nome in rastro:
        r = next(r for r in regras if r["nome"] == nome)
        linhas.append(f'{nome}: como {" e ".join(r["se"])}, concluí {r["entao"]}')
    concluidas = [r["entao"] for r in regras if r["nome"] in rastro and r["entao"] in PRIORIDADE]
    linhas.append(f"ações concluídas: {concluidas}; pela ordem de cautela, venceu {acao}")
    return linhas


def julgar(fatos, palavras):
    """Aplica o motor sem e com incerteza e devolve decisões, rastro, confiança e explicação."""
    fatos_finais, rastro, ciclos = encadear_para_frente(fatos, REGRAS)
    acao_sem = decidir(fatos_finais)
    confianca = encadear_com_confianca(perceber_com_confianca(fatos, palavras), REGRAS)
    acao_com = decidir(confianca)
    if acao_com in confianca and confianca[acao_com] < LIMIAR_CONFIANCA:
        acao_com = "encaminhar_humano"
    return {
        "fatos": sorted(fatos),
        "rastro": rastro,
        "ciclos": ciclos,
        "acao_sem_incerteza": acao_sem,
        "confianca": dict(sorted(confianca.items())),
        "acao_com_incerteza": acao_com,
        "explicacao": explicar(rastro, REGRAS, acao_com),
    }


def verificar_base(regras):
    """Lista as condições que nenhum sensor e nenhuma regra produz (regras que nunca disparam)."""
    produzidos = FATOS_DOS_SENSORES | {r["entao"] for r in regras}
    return [(r["nome"], c) for r in regras for c in r["se"] if c not in produzidos]
