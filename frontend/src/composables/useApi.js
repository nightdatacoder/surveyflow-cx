import axios from 'axios'

const api = axios.create({ baseURL: '/api', timeout: 300000 })

api.interceptors.request.use(config => {
  // Token lu à chaque requête : évite les pertes d'en-tête au démarrage
  const token = localStorage.getItem('access_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers['Authorization'] = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  r => r,
  async error => {
    // Session expirée -> retour au login (sauf pour la tentative de connexion elle-même)
    if (error.response?.status === 401 && !error.config?.url?.includes('/auth/login')) {
      localStorage.clear()
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

export default api
