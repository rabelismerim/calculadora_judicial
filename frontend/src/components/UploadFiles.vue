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

const fileNames = $ref([
  'create_creditors',
  'create_creditors_rj',
  'create_creditors_aj',
])
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
            <QInput
              :model-value="files"
              multiple
              filled
              type="file"
              hint=""
              @update:model-value="val => { files = val }"
            />
          </div>
        </QTabPanel>

        <QTabPanel
          name="historico"
          class="px-4 bg-slate-1"
        >
          <div class="mb-3">
            <div class="font-bold mb-2">
              Histórico de arquivos carregados no sistema
            </div>
          </div>
          Histórico de arquivos aqui
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
