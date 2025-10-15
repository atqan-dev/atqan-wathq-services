/**
 * Wathq API Service types
 */

export type WathqServiceType = 
  | 'commercial-registration'
  | 'company-contract'
  | 'attorney'
  | 'real-estate'
  | 'spl-national-address'
  | 'employee'

export interface WathqService {
  id: string
  name: string
  name_ar: string
  slug: WathqServiceType
  description: string
  description_ar: string
  icon: string
  is_active: boolean
  requires_authentication: boolean
}

export interface WathqApiRequest {
  id: string
  service_type: WathqServiceType
  endpoint: string
  method: 'GET' | 'POST'
  request_data: Record<string, any>
  response_data: Record<string, any>
  status_code: number
  duration_ms: number
  is_success: boolean
  error_message?: string
  created_at: string
  tenant_id?: number
  user_id?: number
}

export interface WathqTestRequest {
  service_type: WathqServiceType
  endpoint: string
  parameters: Record<string, any>
}

export interface WathqTestResponse {
  success: boolean
  data?: any
  error?: string
  duration_ms: number
  timestamp: string
}

export interface WathqRequestLog {
  id: string
  service_type: WathqServiceType
  endpoint: string
  status: 'success' | 'error' | 'pending'
  request_time: string
  response_time?: string
  duration_ms?: number
  tenant_id?: number
  user_id?: number
}

export interface WathqRequestFilters {
  service_type?: WathqServiceType
  status?: 'success' | 'error' | 'pending' | 'all'
  date_from?: string
  date_to?: string
  tenant_id?: number
  search?: string
}

export interface WathqStats {
  total_requests: number
  successful_requests: number
  failed_requests: number
  average_duration_ms: number
  requests_today: number
  requests_this_week: number
  requests_this_month: number
}

// Specific service endpoint types
export interface CommercialRegistrationParams {
  cr_number: string
  date_gregorian?: string
}

export interface CompanyContractParams {
  contract_number: string
  company_cr?: string
}

export interface AttorneyParams {
  authorization_number: string
  identity_number?: string
}

export interface RealEstateParams {
  deed_number: string
  deed_date?: string
}

export interface NationalAddressParams {
  identity_number: string
  address_id?: string
}

export interface EmployeeParams {
  employee_id: string
  company_id?: string
}
