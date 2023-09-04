<script setup lang="ts">
import FilesUploader from '../components/common/FilesUploader.vue'

let files = $ref([] as File[])
const showModal = $ref(true)
const updateFiles = (newFiles: File[]) => files = newFiles

const download = async () => {
  const result = await uploadService.getFilesPathName('project', 'create_creditors')
  saveFile(result, 'download', 'xlsx')
}

const InactiveCreditors = async () => {
  const result = await validationService.getInactive('db559f9b-e678-4066-9f7d-e9404345814f')
  return result
}
</script>

<template>
  <div class="p-4">
    <h1>TESTE</h1>
    <Btn label="Dowload" @click="download" />

    <Btn label="Lista de Credores Inativos" @click="InactiveCreditors" />
    <DropZone
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
    />
  </div>
</template>
