<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue?: boolean
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue', 'update:uploadFiles', 'success'])

const loading = $ref(false)
const form = ref(null as any)

const modalValue = ref(false)
const selectedTab = ref('carregamento')
const filterBy = $ref('')

const tabs = [
  { label: 'Carregamento', value: 'carregamento' },
  { label: 'Histórico', value: 'historico' },
]

const closeModal = () => {
  modalValue.value = false
}

const files: any = $ref(null)
const erros: any = $ref(null)

const fileNames = $ref([
  'create_creditors',
  'create_creditors_rj',
  'create_creditors_aj',
])

const historicFiles: any[] = $ref([
  {
    id: 'db7511f2-3862-4e7d-85d8-8801f5c0349d',
    file: '/media/juca/files/2023/08/14/create_creditors_claim.xlsx',
    name: 'create_creditors_claim.xlsx',
    task: null,
    object_id: '3f51742d-c6b0-4637-9627-fa041c9eafa5',
    errors: [],
  },
  {
    id: 'd0035e4e-fc69-4254-b078-7a44566ed6a8',
    file: '/media/juca/files/2023/08/07/create_creditors_claim.xlsx',
    name: 'create_creditors_claim.xlsx',
    task: null,
    object_id: '3f51742d-c6b0-4637-9627-fa041c9eafa5',
    errors: [],
  },
  {
    id: '82e19e69-baf9-44a9-89b5-224a5410a441',
    file: '/media/juca/files/2023/08/14/create_creditors_claim_-_Copy.xlsx',
    name: 'create_creditors_claim_-_Copy.xlsx',
    task: null,
    object_id: '3f51742d-c6b0-4637-9627-fa041c9eafa5',
    errors: [],
  },
])

const log = (data: string) => console.warn({ data })
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
                v-for="(name, index) in fileNames"
                :key="name"
                class="p-2 border-black/12 bg--base font-bold text--primary flex justify-between cursor-pointer hover:bg--secondary/10 tween"
                :class="{
                  'border-1': index === 0,
                  'border-x-1 border-b-1': index > 0,
                }"
              >
                <div class="flex gap-2 items-center">
                  <div class="i-carbon-xls" />
                  {{ name }}
                </div>
                <div class="i-carbon-document-download" />
              </div>
            </div>
          </div>

          <div class="text-h9" style="font-weight: bold">
            <DropZone
              :types="['xls', 'xlsx']"
              @update:model-value="(val: any) => { files = val }"
              @drop="log"
            />
          </div>
        </QTabPanel>

        <QTabPanel
          name="historico"
          class="px-4 bg-slate-1"
        >
          <div class="mb-3">
            <div class="font-bold mb-2">
              Histórico de arquivos carregados no sistema ({{ fileNames.length }})
            </div>
            <div>
              <div>
                <Accordion
                  v-for="(file, index) in historicFiles"
                  :key="file.id"
                  class="border-black/12 bg--base font-bold flex justify-between mb-2"
                  summary-class="px-2! py-1!"
                >
                  <template #title>
                    <div class="flex items-center gap-2">
                      <div class="i-carbon-xls" />
                      <div>{{ file.name }}</div>
                    </div>
                  </template>
                  <div
                    v-if="file.errors.length > 0"
                    class="flex gap-2 items-center"
                  >
                    <div
                      v-for="error in file.errors"
                      :key="error"
                      class="p-2 flex justify-between"
                      :class="{
                        'border-1': index === 0,
                        'border-x-1 border-b-1': index > 0,
                      }"
                    >
                      <div class="flex gap-2 items-center">
                        <div class="flex gap-2 items-center font-bold text-red-500">
                          Erro {{ index + 1 }}:
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
