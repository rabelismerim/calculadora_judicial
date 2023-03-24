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
  const {
    id = Date.now(),
    timeout,
    message,
  }: any = error
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
