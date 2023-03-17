export default (firstStep: number, stepper: any, form: any) => {
  const data = $ref({
    step: firstStep,
    error: [] as boolean[],
  })

  const setStep = (value: number) => {
    data.step = value
  }
  const validateStep = (ref: number) => {
    const toValidate = form.value?.getValidationComponents()
      .filter(({ $el }: any) => Number($el.parentNode.dataset.step) === ref)
    if (toValidate.length === 0)
      return
    toValidate.forEach((el: any) => el.validate())
    data.error[ref] = toValidate
      .map(({ hasError }: any) => hasError)
      .some((value: boolean) => !!value)
  }
  const validateAll = (count: number) => {
    range(1, count, 1)
      .forEach((step) => {
        data.step = step
        validateStep(step)
      })
  }
  const nextStep = () => {
    validateStep(data.step)
    stepper.value?.next()
  }
  const previousStep = () => {
    validateStep(data.step)
    stepper.value?.previous()
  }
  const clearErrors = () => {
    data.error = []
  }
  const hasError = computed(() => data.error)

  return {
    step: computed({
      get() {
        return data.step
      },
      set(value) {
        data.step = value
      },
    }),
    hasError,
    setStep,
    validateStep,
    validateAll,
    nextStep,
    previousStep,
    clearErrors,
  }
}
