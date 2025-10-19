<template>
  <div>
    <div ref="editorContainer" class="grapesjs-editor" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import type { Editor } from 'grapesjs'

interface Props {
  modelValue?: {
    html?: string
    css?: string
    components?: any[]
    styles?: any[]
  }
  height?: string
  storageKey?: string
  plugins?: any[]
  pluginsOpts?: Record<string, any>
}

const props = withDefaults(defineProps<Props>(), {
  height: '700px',
  storageKey: 'gjs-',
  plugins: () => [],
  pluginsOpts: () => ({}),
})

const emit = defineEmits<{
  'update:modelValue': [value: any]
  'editor:ready': [editor: Editor]
  'change': [data: any]
}>()

const editorContainer = ref<HTMLElement | null>(null)
let editor: Editor | null = null

const initEditor = async () => {
  if (!process.client || !editorContainer.value) return

  try {
    // Dynamically import GrapesJS and plugins
    const grapesjs = (await import('grapesjs')).default
    const grapesjsPresetWebpage = (await import('grapesjs-preset-webpage')).default
    const grapesjsBlocksBasic = (await import('grapesjs-blocks-basic')).default

    // Initialize GrapesJS
    editor = grapesjs.init({
      container: editorContainer.value,
      height: props.height,
      width: 'auto',
      storageManager: {
        type: 'none', // Disable local storage, we'll handle persistence
      },
      plugins: [
        grapesjsPresetWebpage,
        grapesjsBlocksBasic,
        ...props.plugins,
      ],
      pluginsOpts: {
        'grapesjs-preset-webpage': {
          blocks: ['link-block', 'quote', 'text-basic'],
          modalImportTitle: 'Import Template',
          modalImportLabel: '<div style="margin-bottom: 10px; font-size: 13px;">Paste here your HTML/CSS and click Import</div>',
          modalImportContent: (editor: Editor) => {
            return editor.getHtml() + '<style>' + editor.getCss() + '</style>'
          },
        },
        'grapesjs-blocks-basic': {},
        ...props.pluginsOpts,
      },
      canvas: {
        styles: [
          'https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css',
        ],
      },
      blockManager: {
        appendTo: '#blocks',
      },
      styleManager: {
        appendTo: '.styles-container',
        sectors: [
          {
            name: 'General',
            open: true,
            buildProps: ['float', 'display', 'position', 'top', 'right', 'left', 'bottom'],
          },
          {
            name: 'Dimension',
            open: false,
            buildProps: ['width', 'height', 'max-width', 'min-height', 'margin', 'padding'],
          },
          {
            name: 'Typography',
            open: false,
            buildProps: ['font-family', 'font-size', 'font-weight', 'letter-spacing', 'color', 'line-height', 'text-align', 'text-shadow'],
          },
          {
            name: 'Decorations',
            open: false,
            buildProps: ['border-radius-c', 'background-color', 'border-radius', 'border', 'box-shadow', 'background'],
          },
          {
            name: 'Extra',
            open: false,
            buildProps: ['transition', 'perspective', 'transform'],
          },
        ],
      },
      layerManager: {
        appendTo: '.layers-container',
      },
      traitManager: {
        appendTo: '.traits-container',
      },
      selectorManager: {
        appendTo: '.styles-container',
      },
      panels: {
        defaults: [
          {
            id: 'basic-actions',
            el: '.panel__basic-actions',
            buttons: [
              {
                id: 'visibility',
                active: true,
                className: 'btn-toggle-borders',
                label: '<i class="i-heroicons-eye"></i>',
                command: 'sw-visibility',
              },
            ],
          },
          {
            id: 'panel-devices',
            el: '.panel__devices',
            buttons: [
              {
                id: 'device-desktop',
                label: '<i class="i-heroicons-computer-desktop"></i>',
                command: 'set-device-desktop',
                active: true,
                togglable: false,
              },
              {
                id: 'device-tablet',
                label: '<i class="i-heroicons-device-tablet"></i>',
                command: 'set-device-tablet',
                togglable: false,
              },
              {
                id: 'device-mobile',
                label: '<i class="i-heroicons-device-phone-mobile"></i>',
                command: 'set-device-mobile',
                togglable: false,
              },
            ],
          },
          {
            id: 'panel-switcher',
            el: '.panel__switcher',
            buttons: [
              {
                id: 'show-layers',
                active: true,
                label: '<i class="i-heroicons-squares-2x2"></i>',
                command: 'show-layers',
                togglable: false,
              },
              {
                id: 'show-style',
                active: true,
                label: '<i class="i-heroicons-paint-brush"></i>',
                command: 'show-styles',
                togglable: false,
              },
              {
                id: 'show-traits',
                active: true,
                label: '<i class="i-heroicons-cog-6-tooth"></i>',
                command: 'show-traits',
                togglable: false,
              },
            ],
          },
        ],
      },
    })

    // Load initial data if provided
    if (props.modelValue) {
      if (props.modelValue.components) {
        editor.setComponents(props.modelValue.components)
      }
      if (props.modelValue.styles) {
        editor.setStyle(props.modelValue.styles)
      }
      if (props.modelValue.html) {
        editor.setComponents(props.modelValue.html)
      }
      if (props.modelValue.css) {
        editor.setStyle(props.modelValue.css)
      }
    }

    // Set up event listeners
    editor.on('update', () => {
      emitChange()
    })

    // Commands for responsive design
    editor.Commands.add('set-device-desktop', {
      run: (editor) => editor.setDevice('Desktop'),
    })
    editor.Commands.add('set-device-tablet', {
      run: (editor) => editor.setDevice('Tablet'),
    })
    editor.Commands.add('set-device-mobile', {
      run: (editor) => editor.setDevice('Mobile portrait'),
    })

    // Commands for panel switching
    editor.Commands.add('show-layers', {
      run(editor) {
        const openSm = editor.Panels.getButton('views', 'open-sm')
        openSm && openSm.set('active', 0)
      },
    })

    editor.Commands.add('show-styles', {
      run(editor) {
        const openSm = editor.Panels.getButton('views', 'open-sm')
        openSm && openSm.set('active', 1)
      },
    })

    editor.Commands.add('show-traits', {
      run(editor) {
        const openTm = editor.Panels.getButton('views', 'open-tm')
        openTm && openTm.set('active', 1)
      },
    })

    emit('editor:ready', editor)
  } catch (error) {
    console.error('Failed to initialize GrapesJS editor:', error)
  }
}

const emitChange = () => {
  if (!editor) return

  const data = {
    html: editor.getHtml(),
    css: editor.getCss(),
    components: editor.getComponents(),
    styles: editor.getStyle(),
  }

  emit('update:modelValue', data)
  emit('change', data)
}

// Public methods
const getHtml = () => editor?.getHtml() || ''
const getCss = () => editor?.getCss() || ''
const getComponents = () => editor?.getComponents() || []
const getStyles = () => editor?.getStyle() || []
const getEditor = () => editor

defineExpose({
  getHtml,
  getCss,
  getComponents,
  getStyles,
  getEditor,
})

onMounted(() => {
  initEditor()
})

onBeforeUnmount(() => {
  if (editor) {
    editor.destroy()
    editor = null
  }
})

// Watch for external changes
watch(
  () => props.modelValue,
  (newValue) => {
    if (!editor || !newValue) return

    // Only update if the content is different
    const currentHtml = editor.getHtml()
    const currentCss = editor.getCss()

    if (newValue.html && newValue.html !== currentHtml) {
      editor.setComponents(newValue.html)
    }
    if (newValue.css && newValue.css !== currentCss) {
      editor.setStyle(newValue.css)
    }
  },
  { deep: true }
)
</script>

<style>
/* GrapesJS styles */
@import 'grapesjs/dist/css/grapes.min.css';

.grapesjs-editor {
  width: 100%;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
}

/* Custom panel styles */
.panel__basic-actions,
.panel__devices,
.panel__switcher {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
}

.gjs-pn-btn {
  padding: 0.5rem;
  border-radius: 0.375rem;
  cursor: pointer;
  transition: all 0.2s;
}

.gjs-pn-btn:hover {
  background: #e5e7eb;
}

.gjs-pn-btn.gjs-pn-active {
  background: #3b82f6;
  color: white;
}

/* Customize blocks panel */
.gjs-block {
  width: auto !important;
  padding: 0.75rem !important;
  margin: 0.5rem !important;
  border-radius: 0.375rem !important;
  border: 1px solid #e5e7eb !important;
}

.gjs-block:hover {
  border-color: #3b82f6 !important;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1) !important;
}

/* Canvas styles */
.gjs-cv-canvas {
  background: #ffffff;
}

/* Layer manager styles */
.gjs-layer {
  padding: 0.5rem !important;
  border-radius: 0.375rem !important;
}

.gjs-layer:hover {
  background: #f3f4f6 !important;
}

.gjs-layer.gjs-selected {
  background: #eff6ff !important;
  border-left: 3px solid #3b82f6 !important;
}

/* Style manager styles */
.gjs-sm-sector {
  border-radius: 0.375rem !important;
  margin-bottom: 0.5rem !important;
}

.gjs-sm-property {
  padding: 0.5rem !important;
}

/* Trait manager styles */
.gjs-trt-trait {
  padding: 0.5rem !important;
  border-radius: 0.375rem !important;
}

.gjs-trt-trait:hover {
  background: #f3f4f6 !important;
}
</style>
