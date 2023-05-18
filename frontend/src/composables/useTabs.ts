interface Tab {
  name: string
  label: string
}

export default (firstTab: string, tabs: Tab[]) => {
  let tab = $ref(firstTab)
  const currentTab = computed({
    get() {
      return tab
    },
    set(value) {
      tab = value
    },
  })
  const currentTabIndex = computed(() => tabs.findIndex(({ name }) => name === tab))
  const isFirstTab = computed(() => currentTabIndex.value === 0)
  const isLastTab = computed(() => currentTabIndex.value === tabs.length - 1)

  const nextTab = () => {
    const currentIndex = currentTabIndex.value
    const nextIndex = currentIndex === tabs.length - 1 ? 0 : currentIndex + 1
    tab = tabs[nextIndex].name
  }
  const lastTab = () => {
    const currentIndex = currentTabIndex.value
    const nextIndex = currentIndex === 0 ? tabs.length - 1 : currentIndex - 1
    tab = tabs[nextIndex].name
  }

  return {
    currentTab,
    isFirstTab,
    isLastTab,
    nextTab,
    lastTab,
  }
}
