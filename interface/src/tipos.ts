export type Decisao = 'responder' | 'recusar' | 'encaminhar_humano'

export interface Documento {
  id: string
  nota: number
  texto: string
  barrado: boolean
}

export interface Resposta {
  pergunta: string
  modelo: string
  ataque: boolean
  defesa: boolean
  resposta: string | null
  erro_modelo: string | null
  segundos: number | null
  decisao: Decisao
  decisao_sem_incerteza: Decisao
  rastro: string[]
  explicacao: string[]
  confianca: Record<string, number>
  documentos: Documento[]
  acrescimos: { origem: string; destino: string }[]
}
