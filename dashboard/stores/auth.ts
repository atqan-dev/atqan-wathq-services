import { defineStore } from 'pinia'

export interface User {
  id: number
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_super_admin: boolean
  created_at: string
  updated_at: string
}

export interface LoginCredentials {
  username: string
  password: string
}

export interface AuthResponse {
  access_token: string
  token_type: string
  refresh_token?: string
}

export interface UserResponse {
  id: number
  email: string
  first_name: string
  last_name: string
  is_active: boolean
  is_super_admin: boolean
  created_at: string
  updated_at: string
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as User | null,
    token: null as string | null,
    refreshToken: null as string | null,
    isLoading: false as boolean,
  }),

  getters: {
    isAuthenticated: (state) => {
      return !!state.user && !!state.token
    },
  },

  actions: {
    async login(credentials: LoginCredentials): Promise<void> {
      try {
        this.isLoading = true
        
        // Prepare form data for OAuth2 password flow
        const formData = new FormData()
        formData.append('grant_type', 'password')
        formData.append('username', credentials.username)
        formData.append('password', credentials.password)
        formData.append('scope', '')
        formData.append('client_id', 'string')
        formData.append('client_secret', '********')

        const response = await $fetch<AuthResponse>('/api/v1/management/auth/login', {
          method: 'POST',
          body: formData
        })

        // Store tokens in Pinia state
        this.token = response.access_token
        this.refreshToken = response.refresh_token || null

        // Get user information using the access token
        const userResponse = await $fetch<UserResponse>('/api/v1/management/users/me', {
          headers: {
            Authorization: `Bearer ${response.access_token}`
          }
        })

        // Convert UserResponse to User interface
        this.user = {
          id: userResponse.id,
          email: userResponse.email,
          first_name: userResponse.first_name,
          last_name: userResponse.last_name,
          is_active: userResponse.is_active,
          is_super_admin: userResponse.is_super_admin,
          created_at: userResponse.created_at,
          updated_at: userResponse.updated_at
        }

        // Store token in cookie for persistence
        const tokenCookie = useCookie<string | null>('auth-token', {
          default: () => null,
          maxAge: 60 * 60 * 24 * 7, // 7 days
          secure: true,
          sameSite: 'strict'
        })
        tokenCookie.value = response.access_token

        // Store refresh token if provided
        if (response.refresh_token) {
          const refreshCookie = useCookie<string | null>('refresh-token', {
            default: () => null,
            maxAge: 60 * 60 * 24 * 30, // 30 days
            secure: true,
            sameSite: 'strict'
          })
          refreshCookie.value = response.refresh_token
        }

        // Store user in localStorage for persistence
        if (process.client) {
          localStorage.setItem('auth-user', JSON.stringify(this.user))
        }

        
      } catch (error: any) {
        
        throw error
      } finally {
        this.isLoading = false
      }
    },

    async logout(): Promise<void> {
      try {
        // clear token from cookie and local storage
        if (this.token) {
          await $fetch('/api/v1/auth/logout', {
            method: 'POST',
            headers: {
              Authorization: `Bearer ${this.token}`
            }
          }).catch(() => {
            // Ignore logout endpoint errors
            
          })
        }
      } finally {
        // Clear Pinia state
        this.user = null
        this.token = null
        this.refreshToken = null

        // Clear cookies
        const tokenCookie = useCookie('auth-token')
        const refreshCookie = useCookie('refresh-token')
        tokenCookie.value = null
        refreshCookie.value = null

        // Clear localStorage
        if (process.client) {
          localStorage.removeItem('auth-user')
        }

        // Redirect to login
        await navigateTo('/login')
        
        
      }
    },

    async refreshAuthToken(): Promise<boolean> {
      try {
        const refreshCookie = useCookie('refresh-token')
        if (!refreshCookie.value) {
          return false
        }

        const response = await $fetch<AuthResponse>('/api/v1/management/auth/refresh', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: {
            refresh_token: refreshCookie.value
          }
        })

        // Update tokens in Pinia state
        this.token = response.access_token
        this.refreshToken = response.refresh_token || null

        // Get user information using the new access token
        const userResponse = await $fetch<UserResponse>('/api/v1/management/users/me', {
          headers: {
            Authorization: `Bearer ${response.access_token}`
          }
        })

        // Convert UserResponse to User interface
        this.user = {
          id: userResponse.id,
          email: userResponse.email,
          first_name: userResponse.first_name,
          last_name: userResponse.last_name,
          is_active: userResponse.is_active,
          is_super_admin: userResponse.is_super_admin,
          created_at: userResponse.created_at,
          updated_at: userResponse.updated_at
        }

        // Update cookies
        const tokenCookie = useCookie('auth-token')
        tokenCookie.value = response.access_token

        if (response.refresh_token) {
          refreshCookie.value = response.refresh_token
        }

        // Update localStorage
        if (process.client) {
          localStorage.setItem('auth-user', JSON.stringify(this.user))
        }

        
        return true
      } catch (error) {
        
        await this.logout()
        return false
      }
    },

    async initAuth(): Promise<void> {
      const tokenCookie = useCookie('auth-token')
      
      if (tokenCookie.value) {
        try {
          // Try to get user from localStorage first
          if (process.client) {
            const storedUser = localStorage.getItem('auth-user')
            if (storedUser) {
              this.user = JSON.parse(storedUser)
              this.token = tokenCookie.value
              
              // Get refresh token from cookie
              const refreshCookie = useCookie('refresh-token')
              this.refreshToken = refreshCookie.value || null
              
              
              return
            }
          }

          // Verify token and get user info from API
          const response = await $fetch<UserResponse>('/api/v1/management/users/me', {
            headers: {
              Authorization: `Bearer ${tokenCookie.value}`
            }
          })

          // Convert UserResponse to User interface
          this.user = {
            id: response.id,
            email: response.email,
            first_name: response.first_name,
            last_name: response.last_name,
            is_active: response.is_active,
            is_super_admin: response.is_super_admin,
            created_at: response.created_at,
            updated_at: response.updated_at
          }
          this.token = tokenCookie.value
          
          // Get refresh token from cookie
          const refreshCookie = useCookie('refresh-token')
          this.refreshToken = refreshCookie.value || null

          // Store user in localStorage
          if (process.client) {
            localStorage.setItem('auth-user', JSON.stringify(this.user))
          }

          
        } catch (error) {
          
          // Try to refresh token
          const refreshed = await this.refreshAuthToken()
          if (!refreshed) {
            // Clear invalid tokens
            tokenCookie.value = null
            const refreshCookie = useCookie('refresh-token')
            refreshCookie.value = null
            if (process.client) {
              localStorage.removeItem('auth-user')
            }
          }
        }
      }
    },
  },
}) 