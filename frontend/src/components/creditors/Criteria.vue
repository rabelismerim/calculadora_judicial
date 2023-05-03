<script setup lang='ts'>
const props = withDefaults(defineProps<{
  title: string
  name: number
}>(), {
})
let isLoading = $ref(false)
let isEditing = $ref(false)
const onSubmit = async () => {
  isLoading = true
  try {
    // const result = await creditorsService.setRecovering({})
    await delay(2)
    console.warn('teste...')
    isEditing = false
  }
  catch (error) {
    printError('ERROR ON SUBMIT RECOVERING NOTICE:', error)
  }
  finally {
    isLoading = false
  }
}
</script>

<template>
  <AnalisysSheet
    v-model:editing="isEditing"
    v-model:loading="isLoading"
    :name="name"
    title="Ficha de Análise"
    :subtitle="title"
    @submit="onSubmit"
  >
    <div class="pt-6">
      Em desenvolvimento...
    </div>
  </AnalisysSheet>
</template>
