// npm run dev: liga o Ollama e a API (se ainda não estiverem no ar) e depois a interface.
import { spawn } from 'node:child_process'
import { existsSync } from 'node:fs'
import { homedir } from 'node:os'
import { dirname, join } from 'node:path'
import { fileURLToPath } from 'node:url'

const pasta = dirname(fileURLToPath(import.meta.url))
const iniciados = []

// Diz se já há um servidor respondendo no endereço.
async function noAr(url) {
  try {
    await fetch(url, { signal: AbortSignal.timeout(1500) })
    return true
  } catch {
    return false
  }
}

// Inicia um processo auxiliar; se ele não existir, avisa e segue sem ele.
function iniciar(nome, comando, argumentos, opcoes = {}) {
  const processo = spawn(comando, argumentos, { stdio: 'ignore', ...opcoes })
  processo.on('error', (e) => console.log(`Aviso: não consegui iniciar ${nome} (${e.message}).`))
  iniciados.push(processo)
}

if (!(await noAr('http://127.0.0.1:11434/api/version'))) {
  const local = join(homedir(), 'ollama', 'bin', 'ollama')
  console.log('Iniciando o Ollama...')
  iniciar('o Ollama', existsSync(local) ? local : 'ollama', ['serve'], {
    env: { OLLAMA_MAX_LOADED_MODELS: '1', ...process.env },
  })
}

if (!(await noAr('http://127.0.0.1:8000/api/modelos'))) {
  console.log('Iniciando a API (a demonstração fica pronta em cerca de 30 segundos)...')
  iniciar('a API', process.platform === 'win32' ? 'python' : 'python3', [join(pasta, '..', 'codigo', 'servidor.py')])
}

const vite = spawn(process.execPath, [join(pasta, 'node_modules', 'vite', 'bin', 'vite.js'), ...process.argv.slice(2)], {
  cwd: pasta,
  stdio: 'inherit',
})

// Encerra o que este script iniciou.
function encerrar(codigo = 0) {
  iniciados.forEach((p) => p.kill())
  process.exit(codigo)
}

vite.on('exit', (codigo) => encerrar(codigo ?? 0))
process.on('SIGINT', () => encerrar())
process.on('SIGTERM', () => encerrar())
