<script setup lang='ts'>
const props = withDefaults(defineProps<{
  title: string
  name: number
}>(), {
})
const isEditing = $ref(false)
</script>

<template>
  <AnalisysSheet :name="name" title="Ficha de Análise" :subtitle="title">
    <template #side>
      <Btn :label="isEditing ? 'Salvar' : 'Editar'" @click="isEditing = !isEditing" />
    </template>
    <div class="grid">
      {{ isEditing }}
    </div>
  </AnalisysSheet>
</template>
