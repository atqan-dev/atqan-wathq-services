<template>
  <div 
    class="grapesjs-wrapper" 
    :class="{ 
      'dark-theme': isDarkMode, 
      'maximized': isMaximized,
      'sidebar-collapsed': isSidebarCollapsed 
    }"
  >
    <!-- Top Toolbar -->
    <div class="gjs-editor-toolbar">
      <div class="toolbar-section toolbar-left">
        <div class="panel__devices"></div>
      </div>
      
      <div class="toolbar-section toolbar-center">
        <div class="panel__basic-actions"></div>
      </div>
      
      <div class="toolbar-section toolbar-right">
        <div class="panel__switcher"></div>
        
        <!-- Theme Toggle -->
        <button 
          class="toolbar-btn" 
          @click="toggleTheme"
          :title="isDarkMode ? 'Light Mode' : 'Dark Mode'"
        >
          <UIcon :name="isDarkMode ? 'i-heroicons-sun' : 'i-heroicons-moon'" class="w-4 h-4" />
        </button>
        
        <!-- Maximize Toggle -->
        <button 
          class="toolbar-btn" 
          @click="toggleMaximize"
          :title="isMaximized ? 'Exit Fullscreen' : 'Fullscreen'"
        >
          <UIcon :name="isMaximized ? 'i-heroicons-arrows-pointing-in' : 'i-heroicons-arrows-pointing-out'" class="w-4 h-4" />
        </button>
      </div>
    </div>

    <!-- Main Editor Area -->
    <div class="gjs-editor-container">
      <!-- Left Sidebar - Blocks & Assets -->
      <div class="gjs-left-sidebar" v-show="!isSidebarCollapsed">
        <!-- Sidebar Tabs -->
        <div class="sidebar-tabs">
          <button 
            class="sidebar-tab" 
            :class="{ active: activeLeftTab === 'blocks' }"
            @click="activeLeftTab = 'blocks'"
          >
            <UIcon name="i-heroicons-squares-2x2" class="w-4 h-4" />
            <span>{{ t('pdf_editor.blocks', 'Blocks') }}</span>
          </button>
          <button 
            class="sidebar-tab" 
            :class="{ active: activeLeftTab === 'assets' }"
            @click="activeLeftTab = 'assets'"
          >
            <UIcon name="i-heroicons-photo" class="w-4 h-4" />
            <span>{{ t('pdf_editor.assets', 'Assets') }}</span>
          </button>
        </div>
        
        <!-- Blocks Tab -->
        <div v-show="activeLeftTab === 'blocks'" class="sidebar-content">
          <div class="sidebar-search">
            <UInput 
              v-model="blockSearch" 
              icon="i-heroicons-magnifying-glass"
              placeholder="Search blocks..."
              size="sm"
            />
          </div>
          <div id="blocks" class="gjs-blocks-container"></div>
        </div>
        
        <!-- Assets Tab -->
        <div v-show="activeLeftTab === 'assets'" class="sidebar-content">
          <div class="sidebar-search">
            <UInput 
              v-model="assetSearch" 
              icon="i-heroicons-magnifying-glass"
              placeholder="Search assets..."
              size="sm"
            />
          </div>
          <div id="assets" class="gjs-assets-container"></div>
        </div>
      </div>
      
      <!-- Sidebar Toggle Button -->
      <button 
        class="sidebar-toggle-btn left" 
        @click="isSidebarCollapsed = !isSidebarCollapsed"
        :title="isSidebarCollapsed ? 'Show Sidebar' : 'Hide Sidebar'"
      >
        <UIcon :name="isSidebarCollapsed ? 'i-heroicons-chevron-right' : 'i-heroicons-chevron-left'" class="w-4 h-4" />
      </button>

      <!-- Center Canvas -->
      <div class="gjs-canvas-wrapper">
        <div ref="editorContainer" class="grapesjs-editor" />
      </div>

      <!-- Right Sidebar - Settings -->
      <div class="gjs-right-sidebar" v-show="!isRightSidebarCollapsed">
        <!-- Sidebar Tabs -->
        <div class="sidebar-tabs">
          <button 
            class="sidebar-tab" 
            :class="{ active: activeRightTab === 'styles' }"
            @click="activeRightTab = 'styles'"
          >
            <UIcon name="i-heroicons-paint-brush" class="w-4 h-4" />
            <span>{{ t('pdf_editor.styles', 'Styles') }}</span>
          </button>
          <button 
            class="sidebar-tab" 
            :class="{ active: activeRightTab === 'layers' }"
            @click="activeRightTab = 'layers'"
          >
            <UIcon name="i-heroicons-squares-plus" class="w-4 h-4" />
            <span>{{ t('pdf_editor.layers', 'Layers') }}</span>
          </button>
          <button 
            class="sidebar-tab" 
            :class="{ active: activeRightTab === 'traits' }"
            @click="activeRightTab = 'traits'"
          >
            <UIcon name="i-heroicons-cog-6-tooth" class="w-4 h-4" />
            <span>{{ t('pdf_editor.properties', 'Properties') }}</span>
          </button>
        </div>
        
        <div class="sidebar-content">
          <div v-show="activeRightTab === 'styles'" class="styles-container"></div>
          <div v-show="activeRightTab === 'layers'" class="layers-container"></div>
          <div v-show="activeRightTab === 'traits'" class="traits-container"></div>
        </div>
      </div>
      
      <!-- Right Sidebar Toggle Button -->
      <button 
        class="sidebar-toggle-btn right" 
        @click="isRightSidebarCollapsed = !isRightSidebarCollapsed"
        :title="isRightSidebarCollapsed ? 'Show Properties' : 'Hide Properties'"
      >
        <UIcon :name="isRightSidebarCollapsed ? 'i-heroicons-chevron-left' : 'i-heroicons-chevron-right'" class="w-4 h-4" />
      </button>
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

// UI State
const isDarkMode = ref(false)
const isMaximized = ref(false)
const isSidebarCollapsed = ref(false)
const isRightSidebarCollapsed = ref(false)
const activeLeftTab = ref<'blocks' | 'assets'>('blocks')
const activeRightTab = ref<'styles' | 'layers' | 'traits'>('styles')
const blockSearch = ref('')
const assetSearch = ref('')

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value
  // Apply theme to canvas iframe if available
  if (editor) {
    try {
      const canvas = editor.Canvas
      const frame = canvas.getFrameEl()
      if (frame && frame.contentDocument) {
        const body = frame.contentDocument.body
        if (body) {
          body.classList.toggle('dark-mode', isDarkMode.value)
        }
      }
    } catch (e) {
      console.warn('Could not apply theme to canvas:', e)
    }
  }
}

const toggleMaximize = () => {
  isMaximized.value = !isMaximized.value
  if (isMaximized.value) {
    document.documentElement.requestFullscreen?.().catch(() => {})
  } else {
    document.exitFullscreen?.().catch(() => {})
  }
}

const initEditor = async () => {
  if (typeof window === 'undefined' || !editorContainer.value) return

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
        blocks: [], // We'll add custom blocks after init
      },
      assetManager: {
        upload: false,
        multiUpload: false,
        assets: [
          'https://via.placeholder.com/350x250/78c5d6/fff',
          'https://via.placeholder.com/350x250/459ba8/fff',
          'https://via.placeholder.com/350x250/79c267/fff',
          'https://via.placeholder.com/350x250/c5d647/fff',
          'https://via.placeholder.com/350x250/f28c33/fff',
        ],
      } as any,
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

    // Render asset manager in the assets container
    const assetManager = editor.AssetManager
    const assetsContainer = document.getElementById('assets')
    if (assetsContainer && assetManager) {
      assetsContainer.innerHTML = ''
      assetManager.render(assetManager.getAll())
      const amContainer = assetManager.getContainer()
      if (amContainer) {
        assetsContainer.appendChild(amContainer)
      }
    }

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

/* Base Wrapper */
.grapesjs-wrapper {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  border: 1px solid #e5e7eb;
  border-radius: 0.5rem;
  overflow: hidden;
  background: #f9fafb;
  transition: all 0.3s ease;
}

/* Maximized Mode */
.grapesjs-wrapper.maximized {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  border-radius: 0;
  border: none;
}

/* Dark Theme */
.grapesjs-wrapper.dark-theme {
  background: #1f2937;
  border-color: #374151;
}

.grapesjs-wrapper.dark-theme .gjs-editor-toolbar {
  background: #111827;
  border-bottom-color: #374151;
}

.grapesjs-wrapper.dark-theme .gjs-left-sidebar,
.grapesjs-wrapper.dark-theme .gjs-right-sidebar {
  background: #1f2937;
  border-color: #374151;
}

.grapesjs-wrapper.dark-theme .sidebar-tabs {
  background: #111827;
  border-bottom-color: #374151;
}

.grapesjs-wrapper.dark-theme .sidebar-tab {
  color: #9ca3af;
}

.grapesjs-wrapper.dark-theme .sidebar-tab:hover {
  background: #374151;
  color: #f3f4f6;
}

.grapesjs-wrapper.dark-theme .sidebar-tab.active {
  background: #3b82f6;
  color: #ffffff;
}

.grapesjs-wrapper.dark-theme .sidebar-content {
  background: #1f2937;
}

.grapesjs-wrapper.dark-theme .gjs-canvas-wrapper {
  background: #111827;
}

.grapesjs-wrapper.dark-theme .gjs-block {
  background: #374151 !important;
  border-color: #4b5563 !important;
  color: #f3f4f6 !important;
}

.grapesjs-wrapper.dark-theme .gjs-block:hover {
  background: #4b5563 !important;
  border-color: #3b82f6 !important;
}

.grapesjs-wrapper.dark-theme .gjs-block-label {
  color: #f3f4f6 !important;
}

/* Toolbar */
.gjs-editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.75rem 1rem;
  background: #ffffff;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
  gap: 1rem;
}

.toolbar-section {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.toolbar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0.5rem;
  border-radius: 0.375rem;
  border: 1px solid #e5e7eb;
  background: #ffffff;
  cursor: pointer;
  transition: all 0.2s;
  color: #374151;
}

.toolbar-btn:hover {
  background: #f3f4f6;
  border-color: #d1d5db;
}

.dark-theme .toolbar-btn {
  background: #374151;
  border-color: #4b5563;
  color: #f3f4f6;
}

.dark-theme .toolbar-btn:hover {
  background: #4b5563;
  border-color: #6b7280;
}

/* Editor Container */
.gjs-editor-container {
  display: flex;
  flex: 1;
  overflow: hidden;
  min-height: 0;
  position: relative;
}

/* Sidebars */
.gjs-left-sidebar,
.gjs-right-sidebar {
  width: 280px;
  background: #ffffff;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  transition: all 0.3s ease;
}

.gjs-right-sidebar {
  border-right: none;
  border-left: 1px solid #e5e7eb;
}

/* Sidebar Tabs */
.sidebar-tabs {
  display: flex;
  background: #f9fafb;
  border-bottom: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.sidebar-tab {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  padding: 0.75rem 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
  font-size: 0.75rem;
  font-weight: 500;
  border-bottom: 2px solid transparent;
}

.sidebar-tab:hover {
  background: #f3f4f6;
  color: #374151;
}

.sidebar-tab.active {
  background: #ffffff;
  color: #3b82f6;
  border-bottom-color: #3b82f6;
}

.sidebar-tab span {
  display: none;
}

@media (min-width: 1024px) {
  .sidebar-tab span {
    display: inline;
  }
}

/* Sidebar Content */
.sidebar-content {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
  background: #ffffff;
}

.sidebar-search {
  padding: 0.75rem;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

/* Sidebar Toggle Buttons */
.sidebar-toggle-btn {
  position: absolute;
  top: 50%;
  transform: translateY(-50%);
  z-index: 10;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 48px;
  background: #ffffff;
  border: 1px solid #e5e7eb;
  border-radius: 0 0.375rem 0.375rem 0;
  cursor: pointer;
  transition: all 0.2s;
  color: #6b7280;
}

.sidebar-toggle-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.sidebar-toggle-btn.left {
  left: 280px;
}

.sidebar-toggle-btn.right {
  right: 280px;
  border-radius: 0.375rem 0 0 0.375rem;
}

.sidebar-collapsed .sidebar-toggle-btn.left {
  left: 0;
}

.dark-theme .sidebar-toggle-btn {
  background: #374151;
  border-color: #4b5563;
  color: #9ca3af;
}

.dark-theme .sidebar-toggle-btn:hover {
  background: #4b5563;
  color: #f3f4f6;
}

/* Blocks Container */
.gjs-blocks-container,
.gjs-assets-container {
  padding: 0.75rem;
}

/* Canvas Wrapper */
.gjs-canvas-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  background: #e5e7eb;
}

.grapesjs-editor {
  width: 100%;
  height: 100%;
  flex: 1;
}

/* Panel Styles */
.panel__basic-actions,
.panel__devices,
.panel__switcher {
  display: flex;
  gap: 0.25rem;
}

.gjs-pn-btn {
  padding: 0.5rem !important;
  border-radius: 0.375rem !important;
  cursor: pointer !important;
  transition: all 0.2s !important;
  border: 1px solid #e5e7eb !important;
  background: #ffffff !important;
  color: #374151 !important;
}

.gjs-pn-btn:hover {
  background: #f3f4f6 !important;
  border-color: #d1d5db !important;
}

.gjs-pn-btn.gjs-pn-active {
  background: #3b82f6 !important;
  color: white !important;
  border-color: #3b82f6 !important;
}

.dark-theme .gjs-pn-btn {
  background: #374151 !important;
  border-color: #4b5563 !important;
  color: #f3f4f6 !important;
}

.dark-theme .gjs-pn-btn:hover {
  background: #4b5563 !important;
  border-color: #6b7280 !important;
}

/* Blocks Panel */
.gjs-block-category {
  margin-bottom: 0.75rem;
}

.gjs-block-category .gjs-title {
  background: transparent;
  padding: 0.5rem 0;
  font-size: 0.75rem;
  font-weight: 600;
  color: #6b7280;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border: none;
}

.gjs-blocks-c {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 0.5rem;
  padding: 0;
}

.gjs-block {
  width: 100% !important;
  min-height: 70px !important;
  padding: 0.75rem !important;
  margin: 0 !important;
  border-radius: 0.5rem !important;
  border: 1px solid #e5e7eb !important;
  background: #ffffff !important;
  display: flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  cursor: grab !important;
  transition: all 0.2s !important;
  box-shadow: 0 1px 2px 0 rgb(0 0 0 / 0.05) !important;
}

.gjs-block:hover {
  border-color: #3b82f6 !important;
  background: #eff6ff !important;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
  transform: translateY(-2px) !important;
}

.gjs-block:active {
  cursor: grabbing !important;
}

.gjs-block__media {
  margin-bottom: 0.5rem !important;
  font-size: 1.5rem !important;
}

.gjs-block-label {
  font-size: 0.75rem !important;
  color: #374151 !important;
  font-weight: 500 !important;
  text-align: center !important;
  line-height: 1.2 !important;
}

/* Assets Manager */
.gjs-am-assets {
  display: grid !important;
  grid-template-columns: repeat(2, 1fr) !important;
  gap: 0.5rem !important;
}

.gjs-am-asset {
  border-radius: 0.5rem !important;
  overflow: hidden !important;
  border: 2px solid #e5e7eb !important;
  transition: all 0.2s !important;
}

.gjs-am-asset:hover {
  border-color: #3b82f6 !important;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1) !important;
}

.gjs-am-asset-image {
  width: 100% !important;
  height: auto !important;
  aspect-ratio: 4/3 !important;
  object-fit: cover !important;
}

/* Canvas Styles */
.gjs-cv-canvas {
  background: #ffffff;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

/* Layer Manager */
.layers-container,
.styles-container,
.traits-container {
  padding: 0.75rem;
}

.gjs-layer {
  padding: 0.5rem !important;
  border-radius: 0.375rem !important;
  margin-bottom: 0.25rem !important;
  transition: all 0.2s !important;
}

.gjs-layer:hover {
  background: #f3f4f6 !important;
}

.gjs-layer.gjs-selected {
  background: #eff6ff !important;
  border-left: 3px solid #3b82f6 !important;
}

.dark-theme .gjs-layer:hover {
  background: #374151 !important;
}

.dark-theme .gjs-layer.gjs-selected {
  background: #1e3a8a !important;
}

/* Style Manager */
.gjs-sm-sector {
  border-radius: 0.5rem !important;
  margin-bottom: 0.75rem !important;
  border: 1px solid #e5e7eb !important;
  overflow: hidden !important;
}

.gjs-sm-sector .gjs-sm-title {
  background: #f9fafb !important;
  padding: 0.75rem !important;
  font-weight: 600 !important;
  font-size: 0.875rem !important;
  color: #374151 !important;
}

.gjs-sm-properties {
  padding: 0.5rem !important;
}

.gjs-sm-property {
  padding: 0.5rem !important;
  margin-bottom: 0.5rem !important;
}

.dark-theme .gjs-sm-sector {
  border-color: #4b5563 !important;
}

.dark-theme .gjs-sm-sector .gjs-sm-title {
  background: #374151 !important;
  color: #f3f4f6 !important;
}

/* Trait Manager */
.gjs-trt-trait {
  padding: 0.75rem !important;
  border-radius: 0.375rem !important;
  margin-bottom: 0.5rem !important;
  transition: all 0.2s !important;
}

.gjs-trt-trait:hover {
  background: #f3f4f6 !important;
}

.dark-theme .gjs-trt-trait:hover {
  background: #374151 !important;
}

/* Scrollbar Styling */
.sidebar-content::-webkit-scrollbar,
.gjs-blocks-container::-webkit-scrollbar,
.gjs-assets-container::-webkit-scrollbar {
  width: 8px;
}

.sidebar-content::-webkit-scrollbar-track,
.gjs-blocks-container::-webkit-scrollbar-track,
.gjs-assets-container::-webkit-scrollbar-track {
  background: #f3f4f6;
}

.sidebar-content::-webkit-scrollbar-thumb,
.gjs-blocks-container::-webkit-scrollbar-thumb,
.gjs-assets-container::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 4px;
}

.sidebar-content::-webkit-scrollbar-thumb:hover,
.gjs-blocks-container::-webkit-scrollbar-thumb:hover,
.gjs-assets-container::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
}

.dark-theme .sidebar-content::-webkit-scrollbar-track,
.dark-theme .gjs-blocks-container::-webkit-scrollbar-track,
.dark-theme .gjs-assets-container::-webkit-scrollbar-track {
  background: #1f2937;
}

.dark-theme .sidebar-content::-webkit-scrollbar-thumb,
.dark-theme .gjs-blocks-container::-webkit-scrollbar-thumb,
.dark-theme .gjs-assets-container::-webkit-scrollbar-thumb {
  background: #4b5563;
}

.dark-theme .sidebar-content::-webkit-scrollbar-thumb:hover,
.dark-theme .gjs-blocks-container::-webkit-scrollbar-thumb:hover,
.dark-theme .gjs-assets-container::-webkit-scrollbar-thumb:hover {
  background: #6b7280;
}
</style>
