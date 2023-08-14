<script setup>
const show = $ref(true)
</script>

<template>
  <Page>
    <h1>TESTE</h1>
    <template #out>
      <UploadCreditors v-model="show" />
    </template>
  </Page>
</template>
