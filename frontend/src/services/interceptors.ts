export const requestInterceptor = (request: any) => {
  const { method, baseURL = '', url = '', data } = request

  if (data)
    request.data = parseToSnake(data)

  if (import.meta.env.VITE_LOG_REQUEST === 'true')
    printError(`>>>> REQUEST: ${method?.toUpperCase()} ${baseURL + url}`, request)

  return request
}

export const responseInterceptor = (response: any) => {
  const { data, status, config: { method, baseURL = '', url = '' } } = response

  const result = parseToCamel(data)
  if (import.meta.env.VITE_LOG_RESPONSE === 'true')
    printError(`<<<< RESPONSE(${status}): ${method?.toUpperCase()} ${baseURL + url}`, result)

  return result
}

export const errorHandlerInterceptor = async (error: any) => {
  const { message, code, response } = error
  const data = response?.data?.data
  const status = response?.status || 500

  const { errors: dataErrors } = parseToCamel(data || {})
  const errors = dataErrors ? dataErrors?.map(({ detail, attr }: any) => ({ message: detail, attr })) : data
  console.log(response, status)
  printError('ON ERROR:', errors)

  if (errors?.length > 0) {
    for (const error of errors) {
      throwError(error)
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
  }
}
