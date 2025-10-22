// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  compatibilityDate: "2025-05-15",
  devtools: { enabled: true },
  ssr: false,
  experimental: {
    asyncContext: true,
  },
  
  // Server configuration
  devServer: {
    host: "localhost",
    port: 5501,
  },
  runtimeConfig: {
    apiBaseUrl: process.env.NUXT_PRIVATE_API_BASE_URL || 'http://localhost:5500',
    public: {
      apiBase: process.env.NUXT_PUBLIC_API_BASE || 'http://localhost:5500/api/v1',
    },
  },
  // App configuration
  app: {
    head: {
      title: "Atqan Management Wathq API's System",
    },
  },
  // Modules
  modules: [
    "@nuxt/ui",
    "@nuxtjs/tailwindcss",
    "@nuxtjs/color-mode",
    "@nuxt/devtools",
    "@pinia/nuxt",
  ],
  // UI configuration
  ui: {
    global: true,
  },
  // Color mode configuration
  colorMode: {
    preference: "system",
    fallback: "light",
    classSuffix: '',
    classPrefix: '',
  },
  // CSS
  css: ["~/assets/css/main.css"],
  // Source maps
  sourcemap: {
    client: true,
  },
  // Vite configuration
  vite: {
    server: {
      proxy: {
        '/api': {
          target: 'http://localhost:5500',
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
  },
  // Nitro configuration for production
  nitro: {
    routeRules: {
      '/api/**': {
        proxy: 'http://localhost:5500/api/**',
      },
    }
  },
});
