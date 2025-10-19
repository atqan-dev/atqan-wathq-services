<template>
  <div class="grapesjs-wrapper">
    <!-- Top Toolbar -->
    <div class="gjs-editor-toolbar">
      <div class="panel__devices"></div>
      <div class="panel__basic-actions"></div>
      <div class="panel__switcher"></div>
    </div>

    <!-- Main Editor Area -->
    <div class="gjs-editor-container">
      <!-- Left Sidebar - Blocks -->
      <div class="gjs-left-sidebar">
        <div class="gjs-sidebar-header">
          <h3>{{ t('pdf_editor.blocks', 'Blocks') }}</h3>
        </div>
        <div id="blocks" class="gjs-blocks-container"></div>
      </div>

      <!-- Center Canvas -->
      <div class="gjs-canvas-wrapper">
        <div ref="editorContainer" class="grapesjs-editor" />
      </div>

      <!-- Right Sidebar - Panels -->
      <div class="gjs-right-sidebar">
        <div class="gjs-sidebar-header">
          <h3>{{ t('pdf_editor.settings', 'Settings') }}</h3>
        </div>
        <div class="gjs-panels-container">
          <div class="layers-container"></div>
          <div class="styles-container"></div>
          <div class="traits-container"></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import { useI18n } from 'vue-i18n'
import type { Editor } from 'grapesjs'

const { t } = useI18n()

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

    // Add custom blocks for PDF templates
    const blockManager = editor.BlockManager
    
    // Add custom text blocks
    blockManager.add('heading-1', {
      label: 'Heading 1',
      category: 'Typography',
      content: '<h1 style="font-size: 2em; font-weight: bold; margin: 0.5em 0;">Heading 1</h1>',
    })
    
    blockManager.add('heading-2', {
      label: 'Heading 2',
      category: 'Typography',
      content: '<h2 style="font-size: 1.5em; font-weight: bold; margin: 0.5em 0;">Heading 2</h2>',
    })
    
    blockManager.add('paragraph', {
      label: 'Paragraph',
      category: 'Typography',
      content: '<p style="margin: 0.5em 0;">Insert your text here...</p>',
    })
    
    // Add layout blocks
    blockManager.add('2-columns', {
      label: '2 Columns',
      category: 'Layout',
      content: `
        <div style="display: flex; gap: 1rem;">
          <div style="flex: 1; padding: 1rem; border: 1px dashed #ccc;">Column 1</div>
          <div style="flex: 1; padding: 1rem; border: 1px dashed #ccc;">Column 2</div>
        </div>
      `,
    })
    
    blockManager.add('3-columns', {
      label: '3 Columns',
      category: 'Layout',
      content: `
        <div style="display: flex; gap: 1rem;">
          <div style="flex: 1; padding: 1rem; border: 1px dashed #ccc;">Column 1</div>
          <div style="flex: 1; padding: 1rem; border: 1px dashed #ccc;">Column 2</div>
          <div style="flex: 1; padding: 1rem; border: 1px dashed #ccc;">Column 3</div>
        </div>
      `,
    })
    
    // Add table block
    blockManager.add('table', {
      label: 'Table',
      category: 'Layout',
      content: `
        <table style="width: 100%; border-collapse: collapse;">
          <thead>
            <tr>
              <th style="border: 1px solid #ddd; padding: 8px; background: #f3f4f6;">Header 1</th>
              <th style="border: 1px solid #ddd; padding: 8px; background: #f3f4f6;">Header 2</th>
              <th style="border: 1px solid #ddd; padding: 8px; background: #f3f4f6;">Header 3</th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td style="border: 1px solid #ddd; padding: 8px;">Cell 1</td>
              <td style="border: 1px solid #ddd; padding: 8px;">Cell 2</td>
              <td style="border: 1px solid #ddd; padding: 8px;">Cell 3</td>
            </tr>
            <tr>
              <td style="border: 1px solid #ddd; padding: 8px;">Cell 4</td>
              <td style="border: 1px solid #ddd; padding: 8px;">Cell 5</td>
              <td style="border: 1px solid #ddd; padding: 8px;">Cell 6</td>
            </tr>
          </tbody>
        </table>
      `,
    })
    
    // Add variable block for dynamic data
    blockManager.add('variable', {
      label: 'Variable',
      category: 'Dynamic',
      content: '<span style="background: #fef3c7; padding: 2px 6px; border-radius: 3px; font-family: monospace;">{{ variable_name }}</span>',
    })
    
    // Add divider
    blockManager.add('divider', {
      label: 'Divider',
      category: 'Basic',
      content: '<hr style="border: none; border-top: 1px solid #e5e7eb; margin: 1rem 0;" />',
    })
    
    // Add image placeholder
    blockManager.add('image-placeholder', {
      label: 'Image',
      category: 'Media',
      content: '<div style="width: 200px; height: 150px; background: #f3f4f6; display: flex; align-items: center; justify-content: center; border: 2px dashed #d1d5db; border-radius: 4px;"><span style="color: #9ca3af;">Image</span></div>',
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

.grapesjs-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #f9fafb;
}

.gjs-editor-toolbar {
  display: flex;
  gap: 1rem;
  padding: 0.75rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.gjs-editor-container {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
}

.gjs-left-sidebar,
.gjs-right-sidebar {
  width: 250px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.gjs-right-sidebar {
  border-right: none;
  border-left: 1px solid #e5e7eb;
}

.gjs-sidebar-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
  flex-shrink: 0;
}

.gjs-sidebar-header h3 {
  font-size: 0.875rem;
  font-weight: 600;
  color: #374151;
  margin: 0;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.gjs-blocks-container,
.gjs-panels-container {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
}

.gjs-canvas-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #f3f4f6;
}

.grapesjs-editor {
  width: 100%;
  height: 100%;
  flex: 1;
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
.gjs-block-category {
  border-bottom: 1px solid #e5e7eb;
}

.gjs-block-category .gjs-title {
  background: #f9fafb;
  padding: 0.5rem 0.75rem;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.gjs-blocks-c {
  display: grid;
  grid-template-columns: 1fr;
  gap: 0.5rem;
  padding: 0.75rem;
}

.gjs-block {
  width: 100% !important;
  min-height: 60px !important;
  padding: 0.75rem !important;
  margin: 0 !important;
  border-radius: 0.375rem !important;
  border: 1px solid #e5e7eb !important;
  background: #ffffff !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
}

.gjs-block:hover {
  border-color: #3b82f6 !important;
  background: #eff6ff !important;
  box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1) !important;
  transform: translateY(-1px) !important;
}

.gjs-block__media {
  margin-bottom: 0.25rem !important;
}

.gjs-block-label {
  font-size: 0.75rem !important;
  color: #374151 !important;
  font-weight: 500 !important;
  text-align: center !important;
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
