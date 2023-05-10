<script setup lang='ts'>
const attrs = useAttrs() as any

let loading = $ref(false)

const tab = $ref('cred')
const tabFilters = [
  { label: '1. Crédito', value: 'cred' },
  { label: '2. Extrato Contábil', value: 'ext' },
]

const menu = $ref('project')
let project = $ref({} as any)
const loadProject = async () => {
  if (attrs.projectId)
    project = await projectService.getProject(attrs.projectId)
}
let creditor = $ref({} as any)
const loadCreditor = async () => {
  creditor = await creditorsService.getCreditor(attrs.creditorId)
}
const recovering = computed(() => project?.recoverings?.find(({ id }: any) => id === creditor?.recoveringId))
let calculation = $ref({} as any)
const loadCalculation = async () => {
  calculation = await calculationService.getCalculation(attrs.calculationId)
}

const credits = $ref([
  {
    fase: 'judicial',
    creditType: 'INSS',
    onEdict: true,
    description: 'Cálculo base do débito previdenciário relativo ao credor.',
    classType: 'Classe III - Trabalhista',
    calculations: [
      {
        date: '01-01-2013',
        value: 280.05,
        sumula: false,
        taxIndex: 1.6545,
        updatedValue: 365.25,
        statusDisplay: 'Sucesso',
      },
      {
        date: '01-03-2013',
        value: 280.05,
        sumula: false,
        taxIndex: 1.6545,
        updatedValue: 365.25,
        statusDisplay: 'Sucesso',
      },
      {
        date: '01-03-2013',
        value: 280.05,
        sumula: false,
        taxIndex: 1.6545,
        updatedValue: 365.25,
        statusDisplay: 'Erro',
      },
    ],
  },
  {
    fase: 'judicial',
    creditType: 'Salário',
    onEdict: true,
    description: 'Cálculo base do débito Trabalhista devido ao credor.',
    classType: 'Classe III - Trabalhista',
    calculations: [
      {
        date: '01-01-2013',
        value: 2800.0,
        sumula: false,
        taxIndex: 1.6545,
        updatedValue: 3605.25,
        statusDisplay: 'Sucesso',
      },
      {
        date: '01-03-2013',
        value: 2800.0,
        sumula: false,
        taxIndex: 1.6545,
        updatedValue: 3605.25,
        statusDisplay: 'Erro',
      },
    ],
  },
])
const creditsAmount = computed(() => credits.length)
const classesAmount = computed(() => [...new Set(credits.map(({ classType }: any) => classType))].length)
const totalValue = computed(() => credits
  .flatMap(({ calculations }: any) => calculations.map(({ updatedValue }: any) => updatedValue))
  .reduce((acc, curr) => acc + curr, 0))
onMounted(async () => {
  loading = true
  try {
    loadProject()
    loadCreditor()
    loadCalculation()
  }
  catch (error) {
    printError('ERROR ON LOADING CALCULATION:', error)
  }
  finally {
    loading = false
  }
})
</script>

<template>
  <Page
    menu-label="Dados do Projeto"
    :links="[
      { label: 'Projetos', url: '/projetos' },
      { label: project.description, url: `/projeto/${attrs.projectId}` },
      { label: `Cálculo #${calculation?.number}` }]"
  >
    <template #menuheader>
      <BtnToggle
        v-model="menu"
        class="bg--base w-[fit-content]"
        :items="[
          { label: 'Projeto', value: 'project' },
          { label: 'Ficha Técnica', value: 'analysis' },
        ]"
      />
    </template>
    <template #menu>
      <QTabPanels v-model="menu" animated>
        <QTabPanel name="project">
          <ProjectDescription :project="project" />
        </QTabPanel>
        <QTabPanel name="analysis">
          <ProjectDetailCell label="Recuperanda">
            {{ recovering?.entity?.name || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell label="CNPJ">
            {{ formatLegalNumber(recovering?.entity?.legalNumber) || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell label="Credor">
            {{ creditor?.entity?.name || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell :label="creditor?.entity?.legalNumber.length === 11 ? 'CPF' : 'CNPJ'">
            {{ formatLegalNumber(creditor?.entity?.legalNumber) || '-' }}
          </ProjectDetailCell>
        </QTabPanel>
      </QTabPanels>
    </template>
    <Header
      :title="`Cálculo #${calculation?.number || ''} - ${calculation?.creditor?.entity?.name || ''}`"
    >
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Créditos"
        />
      </template>
      <Btn label="Novo Crédito" icon="i-carbon-add-filled" />
    </Header>

    <TabFilter
      v-model="tab"
      :items="tabFilters"
    />

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mb-8">
      <GraphCard
        title="Quantidade de Créditos"
        hint="O Número total dos Créditos neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          {{ creditsAmount }}
        </div>
      </GraphCard>
      <GraphCard
        title="Quantidade de Classes"
        hint="O Número total dos Classes neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          {{ classesAmount }}
        </div>
      </GraphCard>
      <GraphCard
        title="Total Geral de Créditos"
        hint="Somatório dos Créditos neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          {{ totalValue.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}
        </div>
      </GraphCard>
    </div>
    <div class="flex gap-4">
      <Accordion
        v-for="(credit, index) in credits"
        :key="index"
        :title="`Crédito ${index + 1}`"
        :subtitle="credit.classType"
        class="rounded-0"
      >
        <template #header-right>
          <div class="flex gap-2 self-center">
            <Btn label="Editar Crédito" icon="i-carbon-edit" transparent />
            <Btn label="Excluir Crédito" icon="i-carbon-trash-can" transparent />
          </div>
        </template>
        {{ credit }}
      </Accordion>
    </div>
  </Page>
</template>

<style>
[projectId], [calculationId] {
  display: flex;
  flex: 1;
}
</style>
