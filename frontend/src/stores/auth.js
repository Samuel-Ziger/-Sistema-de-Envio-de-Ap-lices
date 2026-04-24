import { defineStore } from 'pinia'
import { api } from '../api'

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token') || null,
    authEnabled: false,
  }),
  getters: {
    isLogged: (s) => !!s.token || !s.authEnabled,
  },
  actions: {
    async carregarStatus() {
      const { data } = await api.get('/api/auth/status')
      this.authEnabled = !!data.auth_enabled
      return data
    },
    async login(username, senha) {
      const { data } = await api.post('/api/auth/login', { username, senha })
      this.token = data.access_token
      this.user = data.user
      localStorage.setItem('access_token', data.access_token)
      return data
    },
    logout() {
      this.token = null
      this.user = null
      localStorage.removeItem('access_token')
    },
  },
})
