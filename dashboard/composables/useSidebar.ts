import { ref, computed } from 'vue'

const isCollapsed = ref(false)
const isMobileMenuOpen = ref(false)

export function useSidebar() {
  // Get sidebar width based on collapse state
  const sidebarWidth = computed(() => isCollapsed.value ? 64 : 256)
  
  // Toggle collapse state
  function toggleCollapse() {
    isCollapsed.value = !isCollapsed.value
    if (typeof window !== 'undefined') {
      localStorage.setItem('sidebar-collapsed', isCollapsed.value.toString())
    }
  }
  
  // Toggle mobile menu
  function toggleMobileMenu() {
    isMobileMenuOpen.value = !isMobileMenuOpen.value
    
    // Lock body scroll when mobile menu is open
    if (typeof window !== 'undefined') {
      if (isMobileMenuOpen.value) {
        document.body.style.overflow = 'hidden'
      } else {
        document.body.style.overflow = ''
      }
    }
  }
  
  // Close mobile menu
  function closeMobileMenu() {
    isMobileMenuOpen.value = false
    if (typeof window !== 'undefined') {
      document.body.style.overflow = ''
    }
  }
  
  // Initialize from localStorage
  function initializeSidebar() {
    if (typeof window !== 'undefined') {
      const savedState = localStorage.getItem('sidebar-collapsed')
      if (savedState !== null) {
        isCollapsed.value = savedState === 'true'
      }
    }
  }
  
  return {
    isCollapsed,
    isMobileMenuOpen,
    sidebarWidth,
    toggleCollapse,
    toggleMobileMenu,
    closeMobileMenu,
    initializeSidebar
  }
}
