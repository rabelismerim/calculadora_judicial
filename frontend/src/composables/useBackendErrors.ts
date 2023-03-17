interface BackendError {
  attr: string
  message: string
}

export default () => {
  let errors: any = $ref({})

  const setError = ({ attr, message }: BackendError) => {
    errors[attr] = message
  }

  const setErrors = ({ errors }: { errors: BackendError[] }) => {
    errors = errors.reduce((acc: any, { attr, message }) => {
      acc[attr] = message
      return acc
    }, {})
  }

  const clearError = (attr: string) => {
    delete errors[attr]
  }

  const clearAll = () => {
    errors = {}
  }

  return {
    errors: computed(() => errors),
    setError,
    setErrors,
    clearError,
    clearAll,
  }
}
