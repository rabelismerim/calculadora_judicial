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

const closeModal = () => {
  modalValue.value = false
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Carregamento em massa de credores"
    modal-class="max-w-300"
    @update:model-value="(value: any) => emit('update:modelValue', value)"
  >
    <div id="q-app" style="min-height: 100vh;">
      <div class="q-pa-md">
        <div class="q-gutter-y-md">
          <QCard>
            <QTabs
              v-model="selectedTab"
              dense
              class="text-grey"
              active-color="primary"
              indicator-color="primary"
              align="justify"
              narrow-indicator
            >
              <QTab name="carregamento" label="Carregamento" />
              <QTab name="historico" label="Histórico" />
            </QTabs>

            <QSeparator />

            <QTabPanels v-model="selectedTab">
              <QTabPanel name="carregamento">
                <div class="text-h9" style="font-weight: bold">
                  Download do template
                </div>
                Templates para download
                <div class="text-h9" style="font-weight: bold">
                  Upload dos arquivos preenchidos
                </div>
              </QTabPanel>

              <QTabPanel name="historico">
                <div class="text-h9" style="font-weight: bold">
                  Histórico de arquivos carregados no sistema
                  <SearchFilter v-model="filterBy" />
                </div>
                Histórico de arquivos aqui
              </QTabPanel>
            </QTabPanels>
          </QCard>
          <Btn
            class="q-mb-md"
            label="Fechar"
            color="primary"
            @click="closeModal"
          />
        </div>
      </div>
    </div>
  </Modal>
</template>
