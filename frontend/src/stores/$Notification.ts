const state = ref(new Map())

interface NotificationOptions {
  message: string
  id?: number | string
  timeout?: number
  type?: string
}

export const notify = ({ message, id = Date.now(), timeout = 20, type = 'success' }: NotificationOptions) => {
  state.value.set(id, {
    message,
    timeout,
    type,
    createdAt: Date.now(),
  })
  if (timeout) {
    setTimeout(() => {
      state.value.delete(id)
    }, timeout * 1000)
  }
}

export const throwError = async (error: any) => {
  let { message } = error
  const {
    code,
    response,
    id = Date.now(),
    timeout,
    response: { data: { data = {} } = {} } = {},
  }: any = error
  const errorMessages = Object.entries(data)
    .map(([key, value]: [string, any]) => [key, value.non_field_errors ? value.non_field_errors : value])

  if (errorMessages.length > 0) {
    for (const [key, msg] of errorMessages) {
      await delay(0.5)
      notify({
        id: key,
        message: msg as string,
        timeout,
        type: 'error',
      })
    }
    return
  }

  if (response?.status === 500 || code === 'ERR_NETWORK')
    message = 'Problemas no Servidor...'
  if (response?.status === 403)
    message = 'Você não está autorizado...'

  notify({ message, id, timeout, type: 'error' })
}

const remove = (id: number | string) => {
  state.value.delete(id)
}

const notifications = computed(() => Array.from(state.value.entries()))

export default {
  notify,
  throwError,
  remove,
  notifications,
}
