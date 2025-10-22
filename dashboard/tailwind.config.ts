import type { Config } from 'tailwindcss'

// Brand palette extracted from the provided logo (3 core colors)
// - brand (primary): periwinkle/indigo
// - brand-deep (secondary): deeper indigo
// - accent: orange
// Shades are approximations to enable utilities like hover, ring, etc.

export default <Partial<Config>>({
  darkMode: 'class',
  content: [
    './components/**/*.{vue,js,ts}',
    './layouts/**/*.vue',
    './pages/**/*.vue',
    './composables/**/*.{js,ts}',
    './plugins/**/*.{js,ts}',
    './app.vue',
  ],
  theme: {
    extend: {
      colors: {
        brand: {
          DEFAULT: '#5A6BEA',
          50: '#eef1fe',
          100: '#e2e7fe',
          200: '#c8d1fb',
          300: '#a6b3f6',
          400: '#8594f0',
          500: '#5A6BEA',
          600: '#4A5FD3', // brand-deep
          700: '#3F51B5',
          800: '#344293',
          900: '#2a3579',
        },
        accent: {
          DEFAULT: '#F28C1B',
          50: '#fff7ea',
          100: '#ffebca',
          200: '#ffd391',
          300: '#ffb956',
          400: '#ffa22a',
          500: '#F28C1B',
          600: '#d87916',
          700: '#b06212',
          800: '#864c0f',
          900: '#6a3c0c',
        },
        // Optional neutral pulled from the deep arc tone
        'brand-deep': '#4A5FD3',
      },
    },
  },
  plugins: [],
})
