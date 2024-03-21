import axios from 'axios'

const headers: any = {
  // TODO: BRING TO USER PREFERENCES
  'Accept-Language': 'pt-BR,pt;q=1',
}

if (import.meta.env.VITE_TOKEN)
  headers.Authorization = `Token ${import.meta.env.VITE_TOKEN}`

const api = axios.create({
  baseURL: import.meta.env.VITE_API_HOST + import.meta.env.VITE_API_BASE_URL,
  withCredentials: true,
  xsrfHeaderName: 'X-CSRFToken',
  xsrfCookieName: 'csrftoken',
  timeout: 100000,
  headers,
})

api.interceptors.request.use((request: any) => {
  const { method, baseURL = '', url = '' } = request

  if (import.meta.env.VITE_LOG_REQUEST === 'true')
    printError(`>>>> REQUEST: ${method?.toUpperCase()} ${baseURL + url}`, request)

  return request
})
api.interceptors.response.use((response: any) => response.data, async (error: any) => {
  const { message, code, response } = error
  const errors = (response?.data?.data?.errors ?? response?.data?.data ?? [])
    .map((error: any) => error?.detail ?? error)
  const status = response?.status || 500

  printError('API FILE ON ERROR:', errors)

  if (errors?.length > 0) {
    for (const error of errors) {
      throwError({ message: error?.detail ?? error })
      await delay(0.5)
    }

    const newError = new Error(message) as any
    newError.errors = errors
    newError.status = status
    newError.code = code
    throw (newError)
  }

  const mainErrors: any = {
    403: 'Você não está autorizado...',
    500: 'Problemas no Servidor...',
    ERR_NETWORK: 'Problemas no Servidor...',
  }
  const mainMessage = mainErrors[status] || mainErrors[code]
  if (mainMessage) {
    throwError({
      id: status,
      message: mainMessage,
    })

    const newError = new Error(mainMessage) as any
    newError.errors = [mainMessage]
    newError.status = status
    newError.code = code
    throw (newError)
  }
})

export default api
