export default function usePagination(list: Ref<any[]>, pageCount: number | Ref<number> | any) {
  const count = computed(() => pageCount?.value ?? pageCount)
  const items = computed(() => list?.value ?? list)

  const data = ref(0)
  const total = computed(() => Math.floor((items.value?.length ?? 0) / count.value ?? 1) || 1)
  const page = computed(() => ({
    total,
    current: data.value + 1,
    items: items.value.slice(data.value * count.value, data.value * count.value + count.value),
  }))
  const next = () => data.value < total.value - 1 && ++data.value
  const previous = () => data.value > 0 && --data.value

  return {
    page,
    next,
    previous,
  }
}
