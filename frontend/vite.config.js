import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    // Stage-safety: bind explicitly to IPv4 loopback on Windows to avoid
    // `localhost` resolving to IPv6 (`::1`) and causing proxy/E2E flakes.
    host: '127.0.0.1',
    // Keep the dev server on a predictable port; if it's taken, fail loudly.
    port: 5173,
    strictPort: true,
    proxy: {
      '/api': {
        // Use IPv4 loopback explicitly to avoid IPv6 (::1) vs IPv4 binding mismatches on Windows.
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      }
    }
  }
})
