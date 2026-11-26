# servidor.py
"""API HTTP do assistente (só biblioteca padrão): POST /api/perguntar e GET /api/modelos."""
import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from assistente import tratar_pergunta
from auditoria import DOCUMENTO_MALICIOSO, ID_MALICIOSO
from busca_palavras import carregar_corpus
from guarda import filtrar_documentos
from modelos import MODELOS, responder

PORTA = 8000
PASTA_CORPUS = Path(__file__).resolve().parent.parent / "corpus"
LIMITE_CORPO = 64 * 1024  # bytes; uma pergunta nunca precisa de mais
MENSAGENS_SEM_MODELO = {
    "recusar": "A guarda recusou esta pergunta; o modelo não foi consultado.",
    "encaminhar_humano": "A guarda encaminhou esta pergunta a uma pessoa; o modelo não foi consultado.",
}


class ErroDePedido(Exception):
    """Pedido inválido: vira resposta HTTP com o código e a mensagem dados."""

    def __init__(self, codigo, mensagem):
        """Guarda o código HTTP e a mensagem do erro."""
        super().__init__(mensagem)
        self.codigo, self.mensagem = codigo, mensagem


def validar(corpo):
    """Extrai (pergunta, modelo, ataque, defesa) do JSON recebido ou levanta ErroDePedido."""
    if not isinstance(corpo, dict):
        raise ErroDePedido(400, "o corpo deve ser um objeto JSON")
    pergunta, modelo = corpo.get("pergunta"), corpo.get("modelo")
    if not isinstance(pergunta, str) or not pergunta.strip():
        raise ErroDePedido(400, "pergunta vazia")
    if modelo not in MODELOS:
        raise ErroDePedido(400, f"modelo desconhecido: {modelo!r}; use um de {MODELOS}")
    ataque, defesa = corpo.get("ataque", False), corpo.get("defesa", True)
    if not isinstance(ataque, bool) or not isinstance(defesa, bool):
        raise ErroDePedido(400, "ataque e defesa devem ser booleanos")
    return pergunta.strip(), modelo, ataque, defesa


def perguntar(pergunta, modelo, ataque, defesa, corpus_base):
    """Roda rede, busca, guarda e (se a guarda liberar) o modelo; devolve o JSON da resposta."""
    corpus = dict(corpus_base)
    if ataque:  # documento envenenado só na memória, como em auditoria.py
        corpus[ID_MALICIOSO] = DOCUMENTO_MALICIOSO
    r = tratar_pergunta(pergunta, corpus)
    documentos = list(r["documentos"])
    if ataque and ID_MALICIOSO not in [i for i, _ in documentos]:
        documentos = documentos[:2] + [(ID_MALICIOSO, 0.0)]  # o atacante garante que o documento chega ao prompt
    barrados = []
    if defesa:
        documentos, barrados = filtrar_documentos(documentos, corpus)
    ids_barrados = {i for i, _ in barrados}
    decisao = r["acao_com_incerteza"]

    resposta, erro_modelo, segundos = MENSAGENS_SEM_MODELO.get(decisao), None, None
    if decisao == "responder":
        saida = responder(modelo, pergunta, [(i, corpus[i]) for i, _ in documentos], com_defesa=defesa)
        resposta, erro_modelo, segundos = saida["texto"] or None, saida["erro"], saida["segundos"]
    return {
        "pergunta": pergunta,
        "modelo": modelo,
        "ataque": ataque,
        "defesa": defesa,
        "resposta": resposta,
        "erro_modelo": erro_modelo,
        "segundos": segundos,
        "decisao": decisao,
        "decisao_sem_incerteza": r["acao_sem_incerteza"],
        "rastro": r["rastro"],
        "explicacao": r["explicacao"],
        "confianca": r["confianca"],
        "documentos": [
            {"id": i, "nota": nota, "texto": corpus[i], "barrado": i in ids_barrados}
            for i, nota in documentos + barrados
        ],
        "acrescimos": [{"origem": o, "destino": d} for o, d in r["acrescimos"]],
    }


def criar_handler(corpus):
    """Cria a classe que atende os pedidos HTTP usando o corpus dado."""
    class Handler(BaseHTTPRequestHandler):
        """Atende as rotas da API."""
        def responder_json(self, codigo, dados):
            """Envia a resposta HTTP em JSON com o código dado."""
            corpo = json.dumps(dados, ensure_ascii=False).encode("utf-8")
            self.send_response(codigo)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(corpo)))
            self.send_header("Access-Control-Allow-Origin", "*")  # a interface roda em outra porta
            self.end_headers()
            self.wfile.write(corpo)

        def do_OPTIONS(self):
            """Responde à consulta de CORS do navegador."""
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.end_headers()

        def do_GET(self):
            """Devolve a lista de modelos em /api/modelos."""
            if self.path == "/api/modelos":
                self.responder_json(200, {"modelos": MODELOS})
            else:
                self.responder_json(404, {"erro": "rota inexistente"})

        def do_POST(self):
            """Valida o pedido de /api/perguntar e devolve o resultado ou o erro."""
            if self.path != "/api/perguntar":
                return self.responder_json(404, {"erro": "rota inexistente"})
            try:
                tamanho = int(self.headers.get("Content-Length") or 0)
                if tamanho > LIMITE_CORPO:
                    raise ErroDePedido(413, "pedido grande demais")
                try:
                    corpo = json.loads(self.rfile.read(tamanho).decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    raise ErroDePedido(400, "JSON inválido")
                pergunta, modelo, ataque, defesa = validar(corpo)
                self.responder_json(200, perguntar(pergunta, modelo, ataque, defesa, corpus))
            except ErroDePedido as e:
                self.responder_json(e.codigo, {"erro": e.mensagem})
            except Exception as e:  # nunca derruba a conexão sem resposta
                self.responder_json(500, {"erro": f"falha interna: {e}"})

        def log_message(self, formato, *args):
            """Escreve o registro de cada pedido na saída de erro."""
            sys.stderr.write("%s - %s\n" % (self.address_string(), formato % args))

    return Handler


def principal():
    """Carrega o corpus, aquece o índice e inicia o servidor."""
    corpus = carregar_corpus(PASTA_CORPUS)
    print("Carregando o modelo de embeddings (demora na primeira vez)...")
    tratar_pergunta("O que é a LGPD?", corpus)  # aquece o índice antes do primeiro pedido
    servidor = ThreadingHTTPServer(("127.0.0.1", PORTA), criar_handler(corpus))
    print(f"API em http://127.0.0.1:{PORTA}  (POST /api/perguntar, GET /api/modelos)")
    try:
        servidor.serve_forever()
    except KeyboardInterrupt:
        print("\nEncerrado.")


if __name__ == "__main__":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    principal()
