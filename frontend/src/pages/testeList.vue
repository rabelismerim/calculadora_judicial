<script setup lang="ts">
import validationService from '../services/validationService'

const emit = defineEmits(['update:modelValue', 'success', 'update:tab'])

const InactiveCreditors = async () => {
  const result = await validationService.getInactive('db559f9b-e678-4066-9f7d-e9404345814f')
  return result
}

let creditorsInactive: any = $ref([])
let creditorsActive: any = $ref([])

const loadCreditorsInactive = async () => {
  try {
    creditorsInactive = await validationService.getInactive('')
  }
  catch (error) {
    printError('ERROR ON LOADING CREDITORS INACTIVE:', error)
  }
}

const loadCreditorsActive = async () => {
  try {
    creditorsActive = await creditorsService.getCreditor('')
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
            Listagem de Credores Ativos ({{ creditorsActive.length }})
          </div>
        </div>
      </QTabPanel>
      <QTabPanel
        name="inativos"
        class="px-4 bg-slate-1"
      >
        <div class="mb-3">
          <div class="font-bold mb-2">
            Listagem de Credores Inativos ({{ creditorsInactive.length }})
          </div>
        </div>
      </QTabPanel>
    </QTabPanels>
  </div>
</template>
