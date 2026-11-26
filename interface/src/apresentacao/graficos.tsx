// Gráficos de barras simples em HTML, usados só pela apresentação.

// Cor fixa por entidade (paleta validada para fundo escuro).
export const AZUL = '#3987e5'
export const VERDE = '#199e70'

export interface Barra {
  nome: string
  valor: number
  total: number
  rotulo?: string
  cor?: string
}

/** Barras horizontais com o valor escrito ao lado; todas partem do zero. */
export function Barras({ barras, larguraNome = 190 }: { barras: Barra[]; larguraNome?: number }) {
  return (
    <ul className="space-y-3">
      {barras.map((b) => (
        <li key={b.nome} className="flex items-center gap-4 text-xl" title={`${b.nome}: ${b.rotulo ?? `${b.valor} de ${b.total}`}`}>
          <span className="shrink-0 text-right text-slate-300" style={{ width: larguraNome }}>
            {b.nome}
          </span>
          <span className="h-6 flex-1 rounded bg-slate-800">
            <span
              className="block h-6 rounded-r"
              style={{ width: `${(b.valor / b.total) * 100}%`, background: b.cor ?? AZUL }}
            />
          </span>
          <span className="w-28 shrink-0 font-semibold tabular-nums text-slate-100">{b.rotulo ?? `${b.valor}/${b.total}`}</span>
        </li>
      ))}
    </ul>
  )
}

/** Legenda com um quadrado de cor por série. */
export function Legenda({ itens }: { itens: { nome: string; cor: string }[] }) {
  return (
    <ul className="flex gap-6 text-lg text-slate-300">
      {itens.map((i) => (
        <li key={i.nome} className="flex items-center gap-2">
          <span className="h-4 w-4 rounded-sm" style={{ background: i.cor }} />
          {i.nome}
        </li>
      ))}
    </ul>
  )
}
