<script setup lang="ts">
let files = $ref([] as File[])
const log = (newFiles: File[]) => files = newFiles

const download = async () => {
  const result = await uploadService.getFilesPathName('project', 'create_creditors')
  saveFile(result, 'download', 'xlsx')
}
</script>

<template>
  <div class="p-4">
    <h1>TESTE</h1>
    <Btn label="Dowload" @click="download" />
    <DropZone
      :types="['xls', 'xlsx']"
      @drop="log"
    />
    <FilesUploader
      v-model="files"
      path="project"
      object-id="db559f9b-e678-4066-9f7d-e9404345814f"
    />
  </div>
</template>
