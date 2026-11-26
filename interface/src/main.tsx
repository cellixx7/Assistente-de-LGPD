import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import { ParaImprimir, Roteiro } from './apresentacao/Apresentacao.tsx'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    {window.location.search === '?imprimir' ? <ParaImprimir /> : window.location.search === '?roteiro' ? <Roteiro /> : <App />}
  </StrictMode>,
)
