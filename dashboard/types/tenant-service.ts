/**
 * Tenant Service type definitions
 */

export interface Service {
  id: string
  name: string
  slug: string
  description: string
  category: 'wathq' | 'other'
  price: string
  is_active: boolean
  requires_approval: boolean
  created_at: string
  updated_at: string
}

export interface TenantService {
  id: number
  tenant_id: number
  service_id: string
  is_active: boolean
  max_users: number
  wathq_api_key: string
  is_approved: boolean
  usage_count: number
  registered_at: string
  approved_at: string | null
  approved_by: number | null
  service: Service
}

export interface TenantServiceFilters {
  tenant_id?: number
  service_id?: string
  is_active?: boolean
  is_approved?: boolean
  category?: 'wathq' | 'other' | 'all'
  search?: string
}

export interface TenantServiceStats {
  total_services: number
  active_services: number
  inactive_services: number
  approved_services: number
  pending_approval: number
  total_usage: number
}
