// Números do artigo, todos produzidos pelos scripts de codigo/. Ao medir de novo, atualize aqui.

export const GUARDA = [
  { nome: '10 casos, sem incerteza', valor: 9, total: 10 },
  { nome: '10 casos, com incerteza', valor: 10, total: 10 },
  { nome: '10 casos, sem a rede', valor: 7, total: 10 },
  { nome: '15 de avaliação', valor: 13, total: 15 },
  { nome: '20 perguntas novas', valor: 16, total: 20 },
]

export const BUSCA = [
  { conjunto: '15 de avaliação (7 com documento)', tfidf: 7, embeddings: 6, total: 7 },
  { conjunto: '20 novas (15 com documento)', tfidf: 10, embeddings: 13, total: 15 },
]

export const TEMPOS = { qwen: 6.68, llama: 7.47 }

// Marcação das 10 respostas de cada modelo (arquivo respostas_marcadas.csv).
export const MARCACAO = {
  qwen: { fiel: 5, semSuporte: 2, recusa: 3 },
  llama: { fiel: 6, semSuporte: 0, recusa: 4 },
}

// Respostas que seguiram a ordem maliciosa, em 36 por condição (2 ataques × 9 perguntas × 2 modelos).
export const AUDITORIA = [
  { nome: 'sem defesa', valor: 9, total: 36 },
  { nome: 'só prompt', valor: 9, total: 36 },
  { nome: 'só guarda', valor: 9, total: 36 },
  { nome: 'prompt + guarda', valor: 7, total: 36 },
]

export const REGRAS = [
  ['R1', 'cita dado pessoal e pede exibição', 'vazamento de dado'],
  ['R2', 'vazamento de dado', 'recusar'],
  ['R3', 'cita incidente e marca ocorrência', 'incidente em curso'],
  ['R4', 'incidente em curso', 'encaminhar a um humano'],
  ['R5', 'pede orientação jurídica', 'encaminhar a um humano'],
  ['R6', 'nenhum termo do domínio', 'fora do domínio'],
  ['R7', 'fora do domínio', 'recusar'],
  ['R8', 'documento encontrado (nota ≥ 0,30)', 'responder'],
]
