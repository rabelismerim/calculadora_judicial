import type { Ref } from 'vue'

interface BackendError {
  attr: string
  message: string
}

export default (errorMessages: Ref) => {
  const setError = ({ attr, message }: BackendError) => {
    errorMessages.value[attr] = message
  }

  const setErrors = ({ errors }: any) => {
    errorMessages.value = errors
      ?.reduce((acc: any, { attr, message }: BackendError) => {
        acc[attr] = message
        return acc
      }, {})
    printError('setErrors', errors)
  }

  const clearError = (attr: string) => {
    if (errorMessages.value[attr])
      delete errorMessages.value[attr]
  }

  const clearAll = () => {
    errorMessages.value = {}
  }

  return {
    setError,
    setErrors,
    clearError,
    clearAll,
  }
}
