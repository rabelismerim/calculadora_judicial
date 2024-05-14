<script setup lang='ts'>
import ReloadBtn from '../common/ReloadBtn.vue'

const props = withDefaults(defineProps<{
  modelValue?: boolean
  projectId: string
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue', 'update:uploadFiles', 'success', 'update:tab', 'update:filter'])

let isLoading = $ref(false)

const selectedTab = ref('carregamento')

const closeModal = () => {
  emit('update:modelValue', false)
}

let templateFiles: any = $ref([])

const loadTemplateNames = async () => {
  try {
    templateFiles = await uploadService.getFilesExamplePath('project')
  }
  catch (error) {
    printError('ERROR ON LOADING FILE EXAMPLE:', error)
  }
}

const downloadTemplate = async (fileName: string) => {
  if (!fileName)
    return
  isLoading = true
  try {
    const result: Blob = await uploadService.getFilesPathName('project', fileName)
    saveFile(result, fileName, 'xlsx')
  }
  catch (error) {
    printError('ERROR ON DOWNLOAD TEMPLATE', error)
  }
  finally {
    isLoading = false
  }
}

let historicFiles: any = $ref([])
const loadHistoricFiles = async () => {
  isLoading = true
  try {
    const files = []
    const filesData = await uploadService.getObjetcId('project', props.projectId)
    for (const file of filesData) {
      const result = await uploadService.getFileDetail(file.id)
      result.name = result.file?.split('/')?.at(-1)

      files.push(result)
    }
    historicFiles = files
  }
  catch (error) {
    printError('ERROR ON LOADING HISTORIC FILES:', error)
  }
  finally {
    isLoading = false
  }
}

const tabs = [
  { label: 'Carregamento', value: 'carregamento' },
  { label: 'Histórico', value: 'historico', onclick: loadHistoricFiles },
]

const fileStatuses = [
  { label: 'Pendente', value: 'PENDING', color: '#c4d600' },
  { label: 'Recebido', value: 'RECEIVED', color: '#007cb0' },
  { label: 'Iniciado', value: 'STARTED', color: '#007cb0' },
  { label: 'Processado', value: 'SUCCESS', color: '#86bc25' },
  { label: 'Falhou', value: 'FAILURE', color: '#d9291c' },
  { label: 'Revogado', value: 'REVOKED', color: '#cccccc' },
  { label: 'Rejeitado', value: 'REJECTED', color: '#cccccc' },
  { label: 'Reprocessando', value: 'RETRY', color: '#c4d600' },
  { label: 'Ignorado', value: 'IGNORED', color: '#cccccc' },
]

const getStatus = (statusName: string) => {
  const status = fileStatuses
    .find(status => status.value === statusName) ?? fileStatuses[0]
  return status
}

onMounted(() => {
  loadTemplateNames()
  loadHistoricFiles()
})

let uploadFiles = $ref([] as File[])
const updateFiles = (newFiles: File[]) => uploadFiles = newFiles
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Carregamento em massa de credores"
    modal-class="max-w-300"
    :loading="isLoading"
    @update:model-value="(value: any) => emit('update:modelValue', value)"
  >
    <div>
      <TabFilter
        v-model="selectedTab"
        :items="tabs"
        class="mb-0!"
      />
      <QTabPanels
        v-model="selectedTab"
      >
        <QTabPanel
          name="carregamento"
          class="px-4 bg-slate-1"
        >
          <div class="mb-3">
            <div class="font-bold mb-2">
              Download do template
            </div>
            <div>
              <div
                v-for="(name, index) in templateFiles"
                :key="name"
                class="p-2 border-black/12 bg--base font-bold text--primary flex justify-between cursor-pointer hover:bg--secondary/10 tween"
                :class="{
                  'border-1': index === 0,
                  'border-x-1 border-b-1': index > 0,
                }"
                @click="downloadTemplate(name)"
              >
                <div class="flex gap-2 items-center">
                  <div class="i-carbon-xls" />
                  {{ name }}
                </div>
                <div
                  class="i-carbon-document-download"
                />
              </div>
            </div>
          </div>

          <div class="text-h9" style="font-weight: bold">
            <DropZone
              :types="['xls', 'xlsx']"
              @drop="updateFiles"
            />
            <FilesUploader
              v-model="uploadFiles"
              path="project"
              :object-id="projectId"
            />
          </div>
        </QTabPanel>

        <QTabPanel
          name="historico"
          class="bg-slate-1 p-0"
        >
          <div class="pb-3 pt-4 px-4 overflow-y-auto max-h-70vh">
            <div class="mb-2 flex items-center gap-4">
              <div class="font-bold text-xl">
                Histórico de arquivos carregados no sistema ({{ historicFiles.length }})
              </div>
              <ReloadBtn @click="loadHistoricFiles" />
            </div>
            <div>
              <div>
                <Accordion
                  v-for="(file) in historicFiles"
                  :key="file.id"
                  class="border-black/12 bg--base font-bold flex justify-between mb-2"
                  summary-class="px-2! py-1!"
                >
                  <template #title>
                    <div class="flex items-center gap-2 justify-between flex-1">
                      <div class="flex gap-2 items-center">
                        <div class="i-carbon-xls" />
                        <div>{{ file.name }}</div>
                      </div>
                      <StatusTag
                        v-if="file.errors?.length"
                        label="Falhou"
                        color="#d9291c"
                      />
                      <StatusTag
                        v-else
                        :label="getStatus(file.task?.status)?.label"
                        :color="getStatus(file.task?.status)?.color"
                      />
                    </div>
                  </template>
                  <div
                    v-if="file.errors.length > 0"
                    class="p-2"
                  >
                    <div
                      v-for="({ error, statusDisplay }, index) in file.errors"
                      :key="index"
                      class="p-2 flex justify-between"
                      :class="{
                        'border-t-1': index > 0,
                      }"
                    >
                      <div class="flex gap-2 items-center">
                        <div class="flex gap-2 items-center font-bold text-red-500">
                          Erro {{ index + 1 }}:
                        </div>
                        <div>
                          {{ error }} - {{ statusDisplay }}
                        </div>
                      </div>
                    </div>
                  </div>
                  <div
                    v-else-if="!file.task?.status"
                    class="p-2 flex justify-center"
                  >
                    Aguardando o processamento em andamento...
                  </div>
                  <div
                    v-else-if="file.task?.status === 'FAILURE'"
                    class="p-2 flex justify-center"
                  >
                    O processamento do arquivo falhou.
                  </div>
                  <div
                    v-else
                    class="p-2 flex justify-center"
                  >
                    O arquivo foi processado com sucesso.
                  </div>
                </accordion>
              </div>
            </div>
          </div>
        </QTabPanel>
      </QTabPanels>
      <div class="p-4 flex justify-end border-t-1 boder-black/12">
        <Btn
          label="Fechar"
          color="primary"
          @click="closeModal"
        />
      </div>
    </div>
  </Modal>
</template>
