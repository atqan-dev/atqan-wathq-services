/**
 * User type definitions for the FastAPI GitHub App Manager
 * Used throughout the application for type safety
 */
export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  name_ar?: string
  logo?: string
  is_active: boolean
  is_superuser: boolean
  tenant_id: number
  created_at: string
  updated_at?: string | null
}

export interface Role {
  id: number
  name: string
  name_ar?: string
  description?: string
  description_ar?: string
  permissions?: Permission[]
}

export interface Permission {
  id: number
  resource_type: string
  action: string
  resource_id?: number | null
  description?: string
  description_ar?: string
}

export interface CreateUserData {
  email: string
  first_name: string
  last_name: string
  name_ar?: string
  logo?: string
  password: string
  is_active?: boolean
  is_superuser?: boolean
}

export interface UpdateUserData {
  first_name?: string
  last_name?: string
  name_ar?: string
  logo?: string
  is_active?: boolean
  is_superuser?: boolean
}

export interface UserStats {
  total_users: number
  active_users: number
  inactive_users: number
  superusers: number
}
