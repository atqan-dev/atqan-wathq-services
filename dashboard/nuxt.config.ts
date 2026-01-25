// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-05-15",
  devtools: { enabled: process.env.NODE_ENV !== 'production' },
  ssr: false,
  experimental: {
    asyncContext: true,
  },
  debug: process.env.NODE_ENV !== 'production',

  // Logging configuration
  logLevel: process.env.NODE_ENV === 'production' ? 'info' : 'verbose',

  // Server configuration
  devServer: {
    host: "localhost",
    port: 4551,
  },
  runtimeConfig: {
    apiBaseUrl: process.env.NUXT_PRIVATE_API_BASE_URL || 'http://localhost:5551',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5551/api/v1',
      wathqApiKey: process.env.NUXT_PUBLIC_WATHQ_API_KEY || '',
    },
  },
  // App configuration
  app: {
    head: {
      title: "TAWTHIQ Management Wathq API's System",
    },
  },
  // Modules
  modules: [
    "@nuxt/ui",
    "@nuxtjs/tailwindcss",
    "@nuxtjs/color-mode",
    "@nuxt/devtools",
    "@pinia/nuxt",
    "@nuxt/image",
  ],
  // UI configuration
  ui: {
    global: true,
  },
  // Color mode configuration
  colorMode: {
    preference: "system",
    fallback: "light",
  },
  // CSS
  css: ["~/assets/css/main.css"],
  // Source maps
  sourcemap: {
    client: true,
  },
  // Image optimization
  image: {
    quality: 80,
    format: ['webp', 'png', 'jpg'],
  },

  // Vite configuration
  vite: {
    server: {
      proxy: {
        '/api': {
          target: process.env.NUXT_PRIVATE_API_BASE_URL || 'http://localhost:5551',
          changeOrigin: true,
          secure: false,
          ws: true,
          configure: (proxy, _options) => {
            proxy.on('error', (err, _req, _res) => {
              console.log('Proxy error:', err);
            });
            proxy.on('proxyReq', (proxyReq, req, _res) => {
              // Forward all headers including authentication
              if (req.headers.cookie) {
                proxyReq.setHeader('cookie', req.headers.cookie);
              }
              if (req.headers.authorization) {
                proxyReq.setHeader('authorization', req.headers.authorization);
              }
            });
            proxy.on('proxyRes', (proxyRes, req, _res) => {
              // Log successful proxy responses
              console.log('Proxy response:', proxyRes.statusCode, req.url);
            });
          }
        },
      },
    },
    vue: {
      script: {
        defineModel: true,
        propsDestructure: true,
      },
    },
    build: {
      chunkSizeWarningLimit: 1000,
    },
  },
  // Nitro configuration for production
  nitro: {
    routeRules: {
      '/api/**': {
        proxy: process.env.NUXT_PRIVATE_API_BASE_URL ? `${process.env.NUXT_PRIVATE_API_BASE_URL}/api/**` : 'http://localhost:5551/api/**',
      },
    }
  },
});
