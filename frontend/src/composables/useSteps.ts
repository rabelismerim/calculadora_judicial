export default (firstStep: number, count: number, stepper: any, form: any) => {
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
  const validateAll = () => {
    range(1, count)
      .forEach((step) => {
        validateStep(step)
      })
  }
  const loadAll = async () => {
    for (const step of range(count, 1)) {
      data.step = step
      await delay(0.01)
    }
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
    loadAll,
    nextStep,
    previousStep,
    clearErrors,
  }
}
