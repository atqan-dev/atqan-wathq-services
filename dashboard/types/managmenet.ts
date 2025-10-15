/**
 * App type definitions for the FastAPI GitHub App Manager
 * Used throughout the application for type safety
 */

export interface UserProfile {
  email: string
  username: string
  full_name: string
  is_active: boolean
  slack_webhook_url: string | null
  github_token: string | null
  id: number
  created_at: string
  updated_at: string
}
