import { useEffect, useState, type FormEvent, type ReactNode } from 'react'
import type { Decisao, Resposta } from './tipos'

const COR_DECISAO: Record<Decisao, string> = {
  responder: 'bg-emerald-500/15 text-emerald-300 ring-emerald-500/40',
  recusar: 'bg-red-500/15 text-red-300 ring-red-500/40',
  encaminhar_humano: 'bg-amber-500/15 text-amber-300 ring-amber-500/40',
}
const MSG_FORA_DO_AR = 'Servidor fora do ar. Rode: python codigo/servidor.py'

function Cartao({ titulo, children }: { titulo: string; children: ReactNode }) {
  return (
    <section className="rounded-xl border border-slate-800 bg-slate-900 p-4">
      <h2 className="mb-3 text-xs font-semibold uppercase tracking-wider text-slate-400">{titulo}</h2>
      {children}
    </section>
  )
}

export default function App() {
  const [modelos, setModelos] = useState<string[]>([])
  const [modelo, setModelo] = useState('')
  const [pergunta, setPergunta] = useState('')
  const [ataque, setAtaque] = useState(false)
  const [carregando, setCarregando] = useState(false)
  const [erro, setErro] = useState<string | null>(null)
  const [r, setR] = useState<Resposta | null>(null)

  useEffect(() => {
    fetch('/api/modelos')
      .then((res) => res.json())
      .then((d: { modelos: string[] }) => {
        setModelos(d.modelos)
        setModelo(d.modelos[0] ?? '')
      })
      .catch(() => setErro(MSG_FORA_DO_AR))
  }, [])

  async function enviar(e: FormEvent) {
    e.preventDefault()
    if (!pergunta.trim()) {
      setErro('Digite uma pergunta.')
      return
    }
    setCarregando(true)
    setErro(null)
    try {
      const res = await fetch('/api/perguntar', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ pergunta, modelo, ataque }),
      })
      const dados = await res.json()
      if (!res.ok) throw new Error(dados.erro ?? `erro HTTP ${res.status}`)
      setR(dados as Resposta)
    } catch (err) {
      setR(null)
      setErro(err instanceof TypeError ? MSG_FORA_DO_AR : (err as Error).message)
    } finally {
      setCarregando(false)
    }
  }

  return (
    <main className="mx-auto max-w-5xl space-y-4 px-4 py-8">
      <header>
        <h1 className="text-2xl font-semibold text-slate-100">Assistente de LGPD</h1>
        <p className="text-sm text-slate-400">Rede semântica, busca, guarda e modelo local, passo a passo.</p>
      </header>

      <form onSubmit={enviar} className="space-y-3 rounded-xl border border-slate-800 bg-slate-900 p-4">
        <textarea
          value={pergunta}
          onChange={(e) => setPergunta(e.target.value)}
          rows={3}
          placeholder="Ex.: Quando preciso do consentimento do titular?"
          className="w-full resize-none rounded-lg border border-slate-700 bg-slate-950 p-3 text-slate-100 placeholder:text-slate-600 focus:border-indigo-500 focus:outline-none"
        />
        <div className="flex flex-wrap items-center gap-4">
          <select
            value={modelo}
            onChange={(e) => setModelo(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-950 px-3 py-2 text-sm"
          >
            {modelos.map((m) => (
              <option key={m}>{m}</option>
            ))}
          </select>
          <label className="flex items-center gap-2 text-sm">
            <input type="checkbox" checked={ataque} onChange={(e) => setAtaque(e.target.checked)} className="accent-red-500" />
            Simular ataque (documento malicioso na base)
          </label>
          <button
            type="submit"
            disabled={carregando || !modelo}
            className="ml-auto rounded-lg bg-indigo-600 px-5 py-2 text-sm font-medium text-white hover:bg-indigo-500 disabled:opacity-50"
          >
            {carregando ? 'Consultando…' : 'Perguntar'}
          </button>
        </div>
      </form>

      {erro && (
        <p role="alert" className="rounded-lg border border-red-500/40 bg-red-500/10 p-3 text-sm text-red-300">
          {erro}
        </p>
      )}

      {r && (
        <div className="space-y-4">
          <Cartao titulo="Decisão e resposta">
            <div className="mb-3 flex flex-wrap items-center gap-2 text-sm">
              <span className={`rounded-full px-3 py-1 font-medium ring-1 ${COR_DECISAO[r.decisao]}`}>{r.decisao}</span>
              {r.decisao_sem_incerteza !== r.decisao && (
                <span className="text-slate-400">sem incerteza seria {r.decisao_sem_incerteza}</span>
              )}
              {r.segundos !== null && <span className="ml-auto text-slate-500">{r.segundos.toFixed(1)} s</span>}
            </div>
            {r.erro_modelo ? (
              <p className="rounded-lg border border-amber-500/40 bg-amber-500/10 p-3 text-sm text-amber-300">
                Modelo indisponível: {r.erro_modelo}
              </p>
            ) : (
              <p className="whitespace-pre-wrap text-slate-100">{r.resposta}</p>
            )}
          </Cartao>

          <div className="grid gap-4 md:grid-cols-2">
            <Cartao titulo="Rastro e explicação">
              <p className="mb-2 font-mono text-sm text-indigo-300">{r.rastro.join(' → ') || 'nenhuma regra disparou'}</p>
              <ul className="space-y-1 text-sm text-slate-300">
                {r.explicacao.map((l) => (
                  <li key={l}>{l}</li>
                ))}
              </ul>
            </Cartao>

            <Cartao titulo="Confiança">
              <ul className="space-y-2">
                {Object.entries(r.confianca).map(([fato, c]) => (
                  <li key={fato} className="text-sm">
                    <div className="flex justify-between text-slate-300">
                      <span>{fato}</span>
                      <span className="tabular-nums">{c.toFixed(2)}</span>
                    </div>
                    <div className="mt-1 h-1.5 rounded bg-slate-800">
                      <div
                        className={`h-1.5 rounded ${c >= 0.7 ? 'bg-emerald-500' : 'bg-amber-500'}`}
                        style={{ width: `${c * 100}%` }}
                      />
                    </div>
                  </li>
                ))}
              </ul>
            </Cartao>
          </div>

          <Cartao titulo="Documentos recuperados">
            <ul className="space-y-3">
              {r.documentos.map((d) => (
                <li
                  key={d.id}
                  className={`rounded-lg border p-3 text-sm ${d.barrado ? 'border-red-500/40 bg-red-500/5' : 'border-slate-800 bg-slate-950'}`}
                >
                  <div className="mb-1 flex items-center gap-2 text-xs">
                    <span className="font-mono text-indigo-300">{d.id}</span>
                    <span className="tabular-nums text-slate-400">nota {d.nota.toFixed(3)}</span>
                    {d.barrado && <span className="rounded bg-red-500/20 px-2 py-0.5 text-red-300">barrado pela guarda</span>}
                  </div>
                  <p className="text-slate-300">{d.texto}</p>
                </li>
              ))}
            </ul>
          </Cartao>

          <Cartao titulo="Acréscimos da rede semântica">
            {r.acrescimos.length ? (
              <ul className="flex flex-wrap gap-2 text-sm">
                {r.acrescimos.map((a) => (
                  <li key={a.origem + a.destino} className="rounded-full bg-slate-800 px-3 py-1">
                    {a.origem} <span className="text-slate-500">→ sinonimo_de →</span> {a.destino}
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-slate-500">Nenhum sinônimo acrescentado.</p>
            )}
          </Cartao>
        </div>
      )}
    </main>
  )
}
