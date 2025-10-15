/**
 * Service type definitions
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
  updated_at: string | null
}

export interface AssignServiceRequest {
  service_id: string
  max_users: number
  wathq_api_key: string
}
