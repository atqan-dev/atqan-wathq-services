export default defineAppConfig({
  ui: {
    primary: 'brand',
    gray: 'cool',
    // Nuxt UI expects a list of color names available from Tailwind theme
    // We've defined 'brand' and 'accent' in tailwind.config.ts
    colors: ['gray', 'brand', 'accent', 'red', 'orange', 'yellow', 'green', 'teal', 'blue', 'indigo', 'violet', 'purple', 'pink']
  } as any
})
