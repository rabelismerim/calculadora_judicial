import axios from 'axios'
import { parseToCamel } from '../composables/utils'
const headers: any = {}

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

api.interceptors.request.use((req) => {
  if (import.meta.env.DEV)
    console.warn('ON REQUEST:', req)
  return req
})

api.interceptors.response.use(
  ({ data }) => {
    const result = parseToCamel(data)
    if (import.meta.env.DEV)
      console.warn('ON RESPONSE:', result)
    return result
  },
  (error) => {
    const { code, response: { data: { data }, status } } = error
    const result = {
      data: parseToCamel(data || {}),
      status,
      code,
    }
    if (import.meta.env.DEV)
      console.warn('ON ERROR:', result)
    throwError(result)
  })

export default api
