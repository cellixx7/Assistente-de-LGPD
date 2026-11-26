# busca_vetorial.py
"""Busca TF-IDF (scikit-learn) e por embeddings (sentence-transformers), ambas por cosseno, top 3."""
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from texto import tokenizar

MODELO_EMBEDDINGS = "paraphrase-multilingual-MiniLM-L12-v2"


def top_k(notas, ids, k=3):
    """Devolve os k melhores como lista de (id, nota), desempatando pelo id."""
    ordem = sorted(range(len(ids)), key=lambda i: (-notas[i], ids[i]))
    return [(ids[i], float(notas[i])) for i in ordem[:k]]


class BuscaTfidf:
    """Índice TF-IDF sobre os radicais do corpus (mesma tokenização do restante do projeto)."""

    def __init__(self, corpus):
        """Calcula a matriz TF-IDF dos documentos do corpus."""
        self.ids = list(corpus)
        self.vetorizador = TfidfVectorizer(analyzer=tokenizar)
        self.matriz = self.vetorizador.fit_transform(corpus.values())

    def buscar(self, pergunta, k=3):
        """Devolve os k documentos com maior cosseno TF-IDF em relação à pergunta."""
        notas = cosine_similarity(self.vetorizador.transform([pergunta]), self.matriz)[0]
        return top_k(notas, self.ids, k)


class BuscaEmbeddings:
    """Índice de embeddings normalizados; o cosseno vira produto interno."""

    def __init__(self, corpus, modelo=MODELO_EMBEDDINGS):
        """Carrega o modelo e transforma cada documento em um vetor normalizado."""
        from sentence_transformers import SentenceTransformer  # importado aqui: carregar o modelo é lento

        self.ids = list(corpus)
        self.modelo = SentenceTransformer(modelo)
        self.matriz = self.modelo.encode(list(corpus.values()), normalize_embeddings=True)

    def buscar(self, pergunta, k=3):
        """Devolve os k documentos com maior cosseno entre os embeddings."""
        vetor = self.modelo.encode([pergunta], normalize_embeddings=True)[0]
        return top_k(self.matriz @ vetor, self.ids, k)
