import axios from 'axios'

const headers: any = {
  // TODO: BRING TO USER PREFERENCES
  accept: 'application/json',
}

if (import.meta.env.VITE_TOKEN)
  headers.Authorization = `Token ${import.meta.env.VITE_TOKEN}`

const api = axios.create({
  baseURL: import.meta.env.VITE_API_HOST + import.meta.env.VITE_ROUTER_BASE_URL,
  withCredentials: true,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
  timeout: 100000,
  headers,
})

api.interceptors.request.use(requestInterceptor)
api.interceptors.response.use(responseInterceptor, errorSilenceHandlerInterceptor)

export default api
