// Moldura da apresentação: tela de 1280x720 ajustada à janela, teclado e versão para imprimir.
import { useEffect, useState } from 'react'
import { PARTES, SLIDES, type Slide } from './slides'

const LARGURA = 1280
const ALTURA = 720

/** Fator que faz o slide caber inteiro na janela, sem a barra de controles. */
function escalaDaJanela() {
  return Math.min(window.innerWidth / LARGURA, (window.innerHeight - 56) / ALTURA)
}

// Um slide com seção, título, conteúdo e número.
function Quadro({ slide, numero, abrirDemo }: { slide: Slide; numero: number; abrirDemo: (p: string) => void }) {
  return (
    <article className="flex flex-col overflow-hidden bg-slate-950 px-16 py-10" style={{ width: LARGURA, height: ALTURA }}>
      <p className={`text-base font-semibold uppercase tracking-widest ${PARTES[slide.parte].texto}`}>
        Parte {slide.parte} · {PARTES[slide.parte].quem} · {PARTES[slide.parte].tema}
      </p>
      <h1 className="mb-6 mt-2 text-4xl font-semibold leading-tight text-slate-50">{slide.titulo}</h1>
      <div className="flex-1">{slide.conteudo(abrirDemo)}</div>
      <div className="flex items-center gap-1 pt-3">
        {SLIDES.map((s, i) => (
          <span key={s.titulo} className={`h-1.5 flex-1 rounded ${PARTES[s.parte].fundo} ${i < numero ? '' : 'opacity-25'}`} />
        ))}
        <span className="ml-3 text-sm tabular-nums text-slate-500">
          {numero} / {SLIDES.length}
        </span>
      </div>
    </article>
  )
}

/** Todos os slides empilhados, um por página: usada para gerar o apresentacao.pdf. */
export function ParaImprimir() {
  return (
    <div className="impressao">
      {SLIDES.map((s, i) => (
        <Quadro key={s.titulo} slide={s} numero={i + 1} abrirDemo={() => {}} />
      ))}
    </div>
  )
}

// Roteiro-guia em texto, gerado a partir das falas dos slides (para imprimir).
export function Roteiro() {
  return (
    <main className="min-h-screen bg-white p-8 text-sm text-black">
      <h1 className="text-2xl font-bold">Roteiro-guia dos slides · 12 minutos</h1>
      {Object.entries(PARTES).map(([n, p]) => (
        <section key={n} className="mt-5">
          <h2 className="border-b-2 border-black pb-1 text-lg font-bold">
            Parte {n} · {p.quem} · {p.tema} ({p.minutos})
          </h2>
          {SLIDES.map((s, i) =>
            String(s.parte) === n ? (
              <div key={s.titulo} className="mt-3 break-inside-avoid">
                <h3 className="font-semibold">
                  Slide {i + 1} · {s.titulo} ({s.tempo})
                </h3>
                <ul className="ml-5 list-disc">
                  {s.fala.map((f) => (
                    <li key={f}>{f}</li>
                  ))}
                </ul>
              </div>
            ) : null,
          )}
        </section>
      ))}
    </main>
  )
}

interface Props {
  indice: number
  mudarIndice: (i: number) => void
  sair: () => void
  abrirDemo: (pergunta: string) => void
}

// Mostra o slide atual e trata teclado e botões.
export default function Apresentacao({ indice, mudarIndice, sair, abrirDemo }: Props) {
  const [escala, setEscala] = useState(escalaDaJanela)

  useEffect(() => {
    const ajustar = () => setEscala(escalaDaJanela())
    window.addEventListener('resize', ajustar)
    return () => window.removeEventListener('resize', ajustar)
  }, [])

  useEffect(() => {
    // Navega, sai ou alterna a tela cheia conforme a tecla.
    function tecla(e: KeyboardEvent) {
      const emBotao = e.target instanceof HTMLButtonElement
      if (['ArrowRight', 'PageDown'].includes(e.key) || (e.key === ' ' && !emBotao)) {
        e.preventDefault()
        mudarIndice(Math.min(indice + 1, SLIDES.length - 1))
      } else if (['ArrowLeft', 'PageUp'].includes(e.key)) {
        e.preventDefault()
        mudarIndice(Math.max(indice - 1, 0))
      } else if (e.key === 'Home') mudarIndice(0)
      else if (e.key === 'End') mudarIndice(SLIDES.length - 1)
      else if (e.key === 'Escape') sair()
      else if (e.key.toLowerCase() === 'f') {
        if (document.fullscreenElement) void document.exitFullscreen()
        else void document.documentElement.requestFullscreen()
      }
    }
    window.addEventListener('keydown', tecla)
    return () => window.removeEventListener('keydown', tecla)
  }, [indice, mudarIndice, sair])

  const botao = 'rounded-lg border border-slate-700 px-4 py-1.5 text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-40'

  return (
    <div className="fixed inset-0 flex flex-col items-center bg-black">
      <div className="flex flex-1 items-center justify-center">
        <div style={{ width: LARGURA * escala, height: ALTURA * escala }}>
          <div style={{ transform: `scale(${escala})`, transformOrigin: 'top left' }}>
            <Quadro slide={SLIDES[indice]} numero={indice + 1} abrirDemo={abrirDemo} />
          </div>
        </div>
      </div>
      <nav className="flex h-14 items-center gap-3">
        <button type="button" className={botao} onClick={() => mudarIndice(indice - 1)} disabled={indice === 0}>
          ← Anterior
        </button>
        <button type="button" className={botao} onClick={() => mudarIndice(indice + 1)} disabled={indice === SLIDES.length - 1}>
          Próximo →
        </button>
        <button type="button" className={botao} onClick={sair}>
          Sair (Esc)
        </button>
        <span className="text-xs text-slate-500">setas para navegar · F para tela cheia</span>
      </nav>
    </div>
  )
}
