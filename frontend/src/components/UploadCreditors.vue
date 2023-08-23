<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue?: boolean
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue', 'update:uploadFiles', 'success', 'update:tab', 'update:filter'])

const loading = $ref(false)
const form = ref(null as any)

const selectedTab = ref('carregamento')

const tabs = [
  { label: 'Carregamento', value: 'carregamento' },
  { label: 'Histórico', value: 'historico' },
]

const closeModal = () => {
  emit('update:modelValue', false)
}

let templateNames: any = $ref([])

const loadTemplateNames = async () => {
  try {
    templateNames = await uploadService.getFilesExamplePath('project')
  }
  catch (error) {
    printError('ERROR ON LOADING FILE EXAMPLE:', error)
  }
}

let isDownloading = $ref(false)
const downloadTemplate = async (fileName: string) => {
  if (!fileName)
    return
  isDownloading = true
  try {
    const result: Blob = await uploadService.getFilesPathName('project', fileName)
    const file = `${fileName}.xlsx`
    console.log({ result, file })
    downloadFile(result, file)
  }
  catch (error) {
    printError('ERROR ON DOWNLOAD TEMPLATE', error)
  }
  finally {
    isDownloading = false
  }
}

const files = $ref([] as File[])

const historicFiles: any = $ref([])
const loadHistoricFiles = async (id: string) => {
  try {
    const filesData = await uploadService.getFileDetail(id)
    historicFiles.value = filesData
  }
  catch (error) {
    printError('ERROR ON LOADING HISTORIC FILES:', error)
  }
}

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
    .find(status => status.value === statusName)
  return status
}

onMounted(() => {
  loadTemplateNames()
  loadHistoricFiles('')
})
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Carregamento em massa de credores"
    modal-class="max-w-300"
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
                v-for="(name, index) in templateNames"
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
              @drop="(val: File[]) => files = val "
            />
          </div>
        </QTabPanel>

        <QTabPanel
          name="historico"
          class="px-4 bg-slate-1"
        >
          <div class="mb-3">
            <div class="font-bold mb-2">
              Histórico de arquivos carregados no sistema ({{ historicFiles.length }})
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
