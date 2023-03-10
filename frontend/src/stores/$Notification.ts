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
    response,
    id = Date.now(),
    timeout,
    response: { data: { data = {} } = {} } = {},
  }: any = error
  const errorMessages = Object.entries(data)
    .flatMap(([,message]) => message || '')

  if (errorMessages.length > 0) {
    for (const msg of errorMessages) {
      await delay(0.5)
      notify({ message: msg as string, id, timeout, type: 'error' })
    }
    return
  }

  if (response?.status === 500)
    message = 'Problemas no Servidor...'
  if (response?.status === 403)
    message = 'Você não está autorizado...'
  if (response?.data?.data?.detail)
    message = response.data.data.detail

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
