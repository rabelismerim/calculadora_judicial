export default function useFilter(list: Ref<any[]>) {
  const items = computed(() => list?.value ?? list)

  const filterBy = ref('')
  const filtered = computed(() => items.value
    .filter((obj: any) => normalizeText(Object.values(flatten(obj)).join(';')).toLowerCase()
      .includes(normalizeText(filterBy.value).toLowerCase())))

  return {
    filterBy,
    filtered,
  }
}
