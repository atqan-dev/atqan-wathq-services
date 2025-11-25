/**
 * Lucide Icons Plugin
 * 
 * Registers commonly used Lucide icons globally.
 * Import additional icons as needed.
 */
import {
  // Navigation & Actions
  Menu,
  X,
  ChevronDown,
  ChevronUp,
  ChevronLeft,
  ChevronRight,
  ArrowLeft,
  ArrowRight,
  ArrowUp,
  ArrowDown,
  ExternalLink,
  MoreHorizontal,
  MoreVertical,
  
  // Common UI
  Search,
  Filter,
  Settings,
  Home,
  User,
  Users,
  Bell,
  Mail,
  Calendar,
  Clock,
  
  // Actions
  Plus,
  Minus,
  Edit,
  Trash2,
  Copy,
  Download,
  Upload,
  Save,
  RefreshCw,
  RotateCcw,
  
  // Status & Feedback
  Check,
  CheckCircle,
  XCircle,
  AlertCircle,
  AlertTriangle,
  Info,
  HelpCircle,
  
  // Security
  Shield,
  ShieldCheck,
  ShieldAlert,
  Lock,
  Unlock,
  Key,
  Eye,
  EyeOff,
  
  // Files & Data
  File,
  FileText,
  Folder,
  FolderOpen,
  Database,
  Server,
  
  // Communication
  MessageSquare,
  Send,
  Phone,
  
  // Misc
  Star,
  Heart,
  Bookmark,
  Tag,
  Link,
  Image,
  Camera,
  Loader2,
  LogOut,
  LogIn,
  QrCode,
  Smartphone,
} from 'lucide-vue-next'

export default defineNuxtPlugin((nuxtApp) => {
  // Register icons as global components
  const icons = {
    // Navigation & Actions
    LucideMenu: Menu,
    LucideX: X,
    LucideChevronDown: ChevronDown,
    LucideChevronUp: ChevronUp,
    LucideChevronLeft: ChevronLeft,
    LucideChevronRight: ChevronRight,
    LucideArrowLeft: ArrowLeft,
    LucideArrowRight: ArrowRight,
    LucideArrowUp: ArrowUp,
    LucideArrowDown: ArrowDown,
    LucideExternalLink: ExternalLink,
    LucideMoreHorizontal: MoreHorizontal,
    LucideMoreVertical: MoreVertical,
    
    // Common UI
    LucideSearch: Search,
    LucideFilter: Filter,
    LucideSettings: Settings,
    LucideHome: Home,
    LucideUser: User,
    LucideUsers: Users,
    LucideBell: Bell,
    LucideMail: Mail,
    LucideCalendar: Calendar,
    LucideClock: Clock,
    
    // Actions
    LucidePlus: Plus,
    LucideMinus: Minus,
    LucideEdit: Edit,
    LucideTrash2: Trash2,
    LucideCopy: Copy,
    LucideDownload: Download,
    LucideUpload: Upload,
    LucideSave: Save,
    LucideRefreshCw: RefreshCw,
    LucideRotateCcw: RotateCcw,
    
    // Status & Feedback
    LucideCheck: Check,
    LucideCheckCircle: CheckCircle,
    LucideXCircle: XCircle,
    LucideAlertCircle: AlertCircle,
    LucideAlertTriangle: AlertTriangle,
    LucideInfo: Info,
    LucideHelpCircle: HelpCircle,
    
    // Security
    LucideShield: Shield,
    LucideShieldCheck: ShieldCheck,
    LucideShieldAlert: ShieldAlert,
    LucideLock: Lock,
    LucideUnlock: Unlock,
    LucideKey: Key,
    LucideEye: Eye,
    LucideEyeOff: EyeOff,
    
    // Files & Data
    LucideFile: File,
    LucideFileText: FileText,
    LucideFolder: Folder,
    LucideFolderOpen: FolderOpen,
    LucideDatabase: Database,
    LucideServer: Server,
    
    // Communication
    LucideMessageSquare: MessageSquare,
    LucideSend: Send,
    LucidePhone: Phone,
    
    // Misc
    LucideStar: Star,
    LucideHeart: Heart,
    LucideBookmark: Bookmark,
    LucideTag: Tag,
    LucideLink: Link,
    LucideImage: Image,
    LucideCamera: Camera,
    LucideLoader2: Loader2,
    LucideLogOut: LogOut,
    LucideLogIn: LogIn,
    LucideQrCode: QrCode,
    LucideSmartphone: Smartphone,
  }

  // Register all icons
  Object.entries(icons).forEach(([name, component]) => {
    nuxtApp.vueApp.component(name, component)
  })
})
