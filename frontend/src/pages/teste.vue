<script setup>
const show = $ref(true)
const log = data => console.warn({ data })
</script>

<template>
  <Page>
    <h1>TESTE</h1>
    <DropZone
      :types="['xls', 'xlsx']"
      @drop="log"
    />
    <template #out>
      <UploadCreditors v-model="show" />
    </template>
  </Page>
</template>
