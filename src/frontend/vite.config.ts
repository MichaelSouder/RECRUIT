import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
// VITE_BASE_PATH: use "/" for root, "/recruit/" for subpath deployment (must end with /).
export default defineConfig({
  base: process.env.VITE_BASE_PATH || '/',
  plugins: [react()],
  server: {
    port: Number(process.env.VITE_DEV_SERVER_PORT) || 5173,
    proxy: {
      '/api': {
        // Use IPv4 loopback explicitly. "localhost" can resolve differently than
        // 127.0.0.1; another app may also bind *:8000 while RECRUIT uses 127.0.0.1:8000.
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})


