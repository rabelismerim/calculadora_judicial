import axios from 'axios'

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

api.interceptors.request.use((request) => {
  const { method, baseURL = '', url = '', data } = request

  if (data)
    request.data = parseToSnake(data)
  if (import.meta.env.VITE_LOG)
    console.warn(`>>>> REQUEST: ${method?.toUpperCase()} ${baseURL + url}`, request)

  return request
})

api.interceptors.response.use(
  (response) => {
    const { data, status, config: { method, baseURL = '', url = '' } } = response

    const result = parseToCamel(data)
    printError(`<<<< RESPONSE(${status}): ${method?.toUpperCase()} ${baseURL + url}`, result)

    return result
  },
  async (error) => {
    const { message, code, response } = error
    const data = response?.data?.data
    const status = response?.status

    const mainErrors: any = {
      403: 'Você não está autorizado...',
      500: 'Problemas no Servidor...',
      ERR_NETWORK: 'Problemas no Servidor...',
    }

    const mainMessage = mainErrors[status] || mainErrors[code]
    if (mainMessage) {
      throwError({
        message: mainMessage,
      })
      return
    }

    const { errors: dataErrors } = parseToCamel(data || {})
    const errors = dataErrors.map(({ detail, attr }: any) => ({ message: detail, attr }))
    printError('ON ERROR:', errors)

    if (errors.length > 0) {
      for (const error of errors) {
        throwError(error)
        await delay(0.5)
      }
    }

    const newError = new Error(message) as any
    newError.errors = errors
    newError.status = status
    newError.code = code

    throw (newError)
  })

export default api
