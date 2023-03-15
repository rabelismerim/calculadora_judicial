import axios from 'axios'
const headers = {}

if (import.meta.env.VITE_TOKEN)
  headers.Authorization = `Token ${import.meta.env.VITE_TOKEN}`

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  withCredentials: true,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
  timeout: 10000,
  headers,
})

export default api
