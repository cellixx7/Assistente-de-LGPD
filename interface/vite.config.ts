import tailwindcss from '@tailwindcss/vite'
import react from '@vitejs/plugin-react'
import { defineConfig } from 'vite'

// O proxy leva /api para o servidor Python (codigo/servidor.py), evitando CORS no desenvolvimento.
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    allowedHosts: ['.app.github.dev'], // endereço das portas encaminhadas pelo Codespaces
    proxy: { '/api': 'http://127.0.0.1:8000' },
  },
})
