// Peças visuais reaproveitadas pelos slides.
import type { ReactNode } from 'react'

// Caixa de destaque com título opcional.
export function Caixa({ titulo, children, tom = 'border-slate-700' }: { titulo?: string; children: ReactNode; tom?: string }) {
  return (
    <div className={`rounded-xl border-2 bg-slate-900 p-5 ${tom}`}>
      {titulo && <h3 className="mb-2 text-xl font-semibold text-slate-100">{titulo}</h3>}
      <div className="text-lg leading-snug text-slate-300">{children}</div>
    </div>
  )
}

// Parágrafo grande do slide.
export function Frase({ children }: { children: ReactNode }) {
  return <p className="text-2xl leading-snug text-slate-300">{children}</p>
}

// Tabela simples com cabeçalho e linhas.
export function Tabela({ cabecalho, linhas }: { cabecalho: string[]; linhas: ReactNode[][] }) {
  return (
    <table className="w-full border-collapse text-left text-lg">
      <thead>
        <tr>
          {cabecalho.map((c) => (
            <th key={c} className="border-b-2 border-slate-700 px-3 py-2 font-semibold text-slate-400">
              {c}
            </th>
          ))}
        </tr>
      </thead>
      <tbody>
        {linhas.map((l, i) => (
          <tr key={i}>
            {l.map((c, j) => (
              <td key={j} className="border-b border-slate-800 px-3 py-1.5 align-top text-slate-200">
                {c}
              </td>
            ))}
          </tr>
        ))}
      </tbody>
    </table>
  )
}

// Um passo numerado do fluxo do sistema.
export function Etapa({ n, nome, detalhe }: { n: number; nome: string; detalhe: string }) {
  return (
    <div className="flex-1 rounded-xl border-2 border-slate-700 bg-slate-900 p-4 text-center">
      <div className="text-sm font-semibold text-indigo-300">{n}</div>
      <div className="text-xl font-semibold text-slate-100">{nome}</div>
      <div className="mt-1 text-base text-slate-400">{detalhe}</div>
    </div>
  )
}

// Botão que abre o assistente com a pergunta pronta.
export function BotaoDemo({ pergunta, abrirDemo }: { pergunta: string; abrirDemo: (p: string) => void }) {
  return (
    <button
      type="button"
      onClick={() => abrirDemo(pergunta)}
      className="rounded-lg bg-indigo-600 px-5 py-3 text-left text-lg font-medium text-white hover:bg-indigo-500"
    >
      ▶ {pergunta}
    </button>
  )
}

// Número grande com legenda.
export function Numero({ valor, legenda }: { valor: string; legenda: string }) {
  return (
    <div className="rounded-xl border-2 border-slate-700 bg-slate-900 p-5 text-center">
      <div className="text-5xl font-semibold text-slate-50">{valor}</div>
      <div className="mt-2 text-lg text-slate-400">{legenda}</div>
    </div>
  )
}

// Etiqueta de um conceito ou fato.
export function Chip({ children, tom = 'border-slate-600 text-slate-100' }: { children: ReactNode; tom?: string }) {
  return <span className={`inline-block rounded-full border-2 bg-slate-900 px-4 py-2 text-lg ${tom}`}>{children}</span>
}

// Seta entre duas etiquetas, com o nome da regra se houver.
export function Seta({ rotulo }: { rotulo?: string }) {
  return (
    <span className="flex flex-col items-center leading-none text-slate-400">
      {rotulo && <span className="text-base font-semibold text-amber-300">{rotulo}</span>}
      <span className="text-3xl">→</span>
    </span>
  )
}

// Sequência de etapas ligadas por setas.
export function Fluxo({ passos }: { passos: string[][] }) {
  return (
    <div className="flex items-center gap-2">
      {passos.map(([nome, detalhe], i) => (
        <div key={nome} className="flex flex-1 items-center gap-2">
          <Etapa n={i + 1} nome={nome} detalhe={detalhe} />
          {i < passos.length - 1 && <span className="text-2xl text-slate-500">→</span>}
        </div>
      ))}
    </div>
  )
}
