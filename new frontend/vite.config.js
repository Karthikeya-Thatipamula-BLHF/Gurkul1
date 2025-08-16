import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig(({ command, mode }) => {
  const isProduction = mode === 'production'

  return {
    plugins: [react(), tailwindcss()],

    // Build configuration
    build: {
      outDir: 'dist',
      sourcemap: !isProduction,
      minify: isProduction ? 'esbuild' : false,
      rollupOptions: {
        output: {
          manualChunks: {
            vendor: ['react', 'react-dom'],
            ui: ['lucide-react', 'react-icons'],
            utils: ['lodash', 'uuid']
          }
        }
      },
      chunkSizeWarningLimit: 1000
    },

    // Environment variables
    define: {
      __APP_VERSION__: JSON.stringify(process.env.npm_package_version || '1.0.0'),
      __BUILD_TIME__: JSON.stringify(new Date().toISOString())
    },

    // Server configuration (development only)
    server: {
      host: '0.0.0.0',
      port: 3000,
      historyApiFallback: true,
      proxy: isProduction ? {} : {
        // Development proxies only
        '/api': {
          target: process.env.VITE_API_BASE_URL || 'http://localhost:8000',
          changeOrigin: true,
          rewrite: (path) => path.replace(/^\/api/, '')
        }
      }
    },

    // Preview configuration
    preview: {
      host: '0.0.0.0',
      port: 3000
    },

    // Optimization
    optimizeDeps: {
      include: ['react', 'react-dom', 'react-router-dom']
    }
  }
})
