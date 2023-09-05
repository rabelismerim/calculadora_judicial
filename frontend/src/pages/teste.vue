<script setup lang="ts">
import TesteList from '../components/TestList.vue'

// let files = $ref([] as File[])
// const showModal = $ref(true)
// const updateFiles = (newFiles: File[]) => files = newFiles

// const download = async () => {
//   const result = await uploadService.getFilesPathName('project', 'create_creditors')
//   saveFile(result, 'download', 'xlsx')
// }
</script>

<template>
  <div class="p-4">
    <h1>TESTE</h1>

    <TesteList project-id="db559f9b-e678-4066-9f7d-e9404345814f" creditor-id="bce5b96d-23c9-4b93-b7c6-9501771cee2b" />
    <!-- <DropZone
      :types="['xls', 'xlsx']"
      @drop="updateFiles"
    />
    <FilesUploader
      v-model="files"
      path="project"
      object-id="db559f9b-e678-4066-9f7d-e9404345814f"
    />
    <UploadCreditors
      v-model="showModal"
      project-id="db559f9b-e678-4066-9f7d-e9404345814f"
    /> -->
  </div>
</template>
