import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react(), tailwindcss()],
  server: {
    port: 5173,
    // Le frontend appelle des chemins relatifs ("/api/..."), Vite les
    // redirige vers le backend FastAPI. Pas besoin de gerer une URL
    // d'API differente en dev : ca marche tel quel des que les deux
    // serveurs tournent (voir README pour le lancement des deux).
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
