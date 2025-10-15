/**
 * Tenant and Service History type definitions
 * Used throughout the application for type safety
 */

export interface Tenant {
  id: number
  name: string
  name_ar?: string
  slug: string
  description?: string
  is_active: boolean
  max_users: number
  users_count?: number
  logo?: string
  created_at: string
  updated_at?: string
}

export interface ServiceHistory {
  id: string
  tenant_id: number
  user_id: number
  service_slug: string
  endpoint: string
  method: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE'
  status_code: number
  request_data: Record<string, any>
  response_body: Record<string, any>
  duration_ms: number
  fetched_at: string
  is_active?: boolean
}

export interface CreateTenantData {
  name: string
  name_ar?: string
  slug: string
  description?: string
  is_active?: boolean
  max_users?: number
  logo?: string
}

export interface UpdateTenantData {
  name?: string
  name_ar?: string
  slug?: string
  description?: string
  is_active?: boolean
  max_users?: number
  logo?: string
}

export interface TenantStats {
  total_tenants: number
  active_tenants: number
  inactive_tenants: number
  total_users: number
}

export interface ServiceHistoryStats {
  total_calls: number
  successful_calls: number
  failed_calls: number
  average_duration_ms: number
}
