<script setup lang='ts'>
const attrs = useAttrs() as any

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
onMounted(() => {
  loadProject()
})
</script>

<template>
  <Page
    menu-label="Dados do Projeto"
    :links="[
      { label: 'Projetos', url: '/projetos' },
      { label: project.description, url: `/projeto/${attrs.projectId}` },
      { label: `Cálculo #${attrs.calculationId}` }]"
  >
    <template #menuheader>
      <BtnToggle
        v-model="menu"
        :items="[
          { label: 'Projeto', value: 'project' },
          { label: 'Recup.', value: 'recovering' },
          { label: 'Credor', value: 'creditor' },
        ]"
      />
    </template>
    <template #menu>
      <QTabPanels v-model="menu" animated>
        <QTabPanel name="project">
          <ProjectDetailCell label="Engagement">
            <div v-for="(engagement, index) in project?.engagement?.numbers" :key="index">
              {{ engagement }}
            </div>
          </ProjectDetailCell>

          <ProjectDetailCell label="Sócio Jurídico">
            {{ project?.legalPartner?.fullName || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Sócio Financeiro">
            {{ project?.financialPartner?.fullName || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Gerente Jurídico">
            {{ project?.legalManager?.fullName || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Gerente Financeiro">
            {{ project?.financialManager?.fullName || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Gerente de Cálculo">
            {{ project?.calculationManager?.fullName || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Recuperandas">
            <div
              v-for="recovering in project?.recoverings as any[]"
              :key="recovering.id"
              class="mb-2"
            >
              <div class="font-bold">
                {{ recovering.entity.name }}
              </div>
              <div>{{ formatLegalNumber(recovering.entity.legalNumber) }}</div>
            </div>
          </ProjectDetailCell>

          <ProjectDetailCell label="Data de Pedido de Recuperação">
            {{ formatDateFromBackend(project?.projectStart) || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Número do Processo Principal">
            {{ project?.processNumber || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Juiz">
            {{ toProperName(project?.judge?.description || '') || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Advogado">
            {{ toProperName(project?.lawyer?.description || '') || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Comarca">
            {{ project?.region?.description || '-' }}
          </ProjectDetailCell>

          <ProjectDetailCell label="Vara">
            {{ project?.court?.description || '-' }}
          </ProjectDetailCell>
        </QTabPanel>
        <QTabPanel name="recovering">
          Recuperanda...
        </QTabPanel>
        <QTabPanel name="creditor">
          Credor...
        </QTabPanel>
      </QTabPanels>
    </template>
    <Header :title="`Cálculo #${attrs.calculationId}`">
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
