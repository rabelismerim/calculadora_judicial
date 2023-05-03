<script setup lang='ts'>
const props = withDefaults(defineProps<{
  title: string
  name: number
  defaultValue?: any
}>(), {
  defaultValue: () => ({}),
})
let isLoading = $ref(false)
let isEditing = $ref(false)

let dataValue: any = $ref(null)
const data = computed({
  get() {
    return dataValue || props.defaultValue
  },
  set(newValue) {
    dataValue = newValue
  },
})
const onSubmit = async () => {
  isLoading = true
  try {
    const result = await creditorsService.setNotice(data.value)
    console.warn(result)
    isEditing = false
  }
  catch (error) {
    printError('ERROR ON SUBMIT RECOVERING NOTICE:', error)
  }
  finally {
    isLoading = false
  }
}
const onReset = () => {
  data.value = null
}
</script>

<template>
  <AnalisysSheet
    v-model:editing="isEditing"
    v-model:loading="isLoading"
    :name="name"
    title="Ficha de Análise"
    :subtitle="title"
    @reset="onReset"
    @submit="onSubmit"
  >
    <div class="grid">
      isEditing: {{ isEditing }}, isLoading: {{ isLoading }}
      data: {{ data }}
    </div>
  </AnalisysSheet>
</template>
