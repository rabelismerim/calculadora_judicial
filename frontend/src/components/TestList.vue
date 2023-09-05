<script setup lang="ts">
import validationService from '../services/validationService'
import creditorsService from '../services/creditorsService'

const props = withDefaults(defineProps<{
  modelValue?: boolean
  projectId: string
}>(), {
  modelValue: false,
})

const emit = defineEmits(['update:modelValue', 'success', 'update:tab'])

let creditorsInactive = $ref([])
let creditorsActive = $ref([])

const loadCreditorsInactive = async () => {
  try {
    creditorsInactive = await validationService.getInactive(props.projectId)
    console.log('RETORNO:', { creditorsInactive })
  }
  catch (error) {
    printError('ERROR ON LOADING CREDITORS INACTIVE:', error)
  }
}

const loadCreditorsActive = async () => {
  try {
    creditorsActive = await creditorsService.getCreditors(props.projectId)
    console.log('RETORNO:', { creditorsActive })
  }
  catch (error) {
    printError('ERROR ON LOADING CREDITORS ACTIVE', error)
  }
}

const selectedTab = ref('ativos')

const tabs = [
  { label: 'Ativos', value: 'ativos' },
  { label: 'Inativos', value: 'inativos' },
]

onMounted(() => {
  loadCreditorsActive()
  loadCreditorsInactive()
})
</script>

<template>
  <div class="p-4">
    <h1>TESTE LISTA CREDORES ATIVOS E INATIVOS</h1>

    <TabFilter
      v-model="selectedTab"
      :items="tabs"
      class="mb-0!"
    />
    <QTabPanels
      v-model="selectedTab"
    >
      <QTabPanel
        name="ativos"
        class="px-4 bg-slate-1"
      >
        <div class="mb-3">
          <div class="font-bold mb-2">
            Listagem de Credores Ativos ({{ creditorsActive?.length }})
          </div>
        </div>
      </QTabPanel>
      <QTabPanel
        name="inativos"
        class="px-4 bg-slate-1"
      >
        <div class="mb-3">
          <div class="font-bold mb-2">
            Listagem de Credores Inativos ({{ creditorsInactive?.length }})
          </div>
        </div>
      </QTabPanel>
    </QTabPanels>
  </div>
</template>
