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
      <UploadCreditors
        v-model="show"
        project-id="34d7ee0e-3a3f-4b7b-98d0-e27a388b7491"
      />
    </template>
  </Page>
</template>
