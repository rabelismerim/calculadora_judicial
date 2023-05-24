<script setup lang="ts">
const attrs = useAttrs() as any
const router = useRouter()

interface Project {
  recoverings: {
    id: string
    entity: any
    creditors: any[]
  }[]
  engagement: {
    numbers: any[]
  }
  participants: {
    user: any
  }[]
  [key: string]: any
}

let loading = $ref(false)
const filterBy = $ref('')
const showParticipants = $ref(false)
let project = $ref({} as Project)
const showEditingProject = $ref(false)

const tab = $ref('all')
const tabFilters = [
  { label: 'Todos', value: 'all' },
  { label: 'A Revisar', value: 'd' },
  { label: 'A Aprovar', value: 'c' },
  { label: 'Aprovado', value: 'p' },
]

const filteredRecoverings = computed(() => {
  if (tab === 'all')
    return project?.recoverings || []
  return project?.recoverings?.filter(() => false)
})

const loadProject = async () => {
  loading = true
  try {
    project = await projectService.getProject(attrs.projectId)
  }
  catch (error) {
    printError(`ERROR ON LOAD PROJECT ${attrs.projectId}:`, error)
  }
  finally {
    loading = false
  }
}

const calculationForm: any = ref(null)
let showCreateNewCalculation = $ref(false)
let newCalculation: any = $ref({
  isAdm: true,
})
const openNewCalculation = (creditor: any) => {
  const { id } = creditor
  newCalculation.creditorId = id
  showCreateNewCalculation = true
}
const openCalculation = (creditorId: string, calculationId: string) =>
  router.push({ path: `/projeto/${project.id}/credor/${creditorId}/calculo/${calculationId}` })
const createNewCalculation = async () => {
  loading = true
  try {
    const { creditorId } = newCalculation
    const { id } = await calculationService.newCalculation(newCalculation)
    openCalculation(creditorId, id)
  }
  catch (error) {
    printError('ERROR ON CREATE NEW CALCULATION:', error)
  }
  finally {
    loading = false
  }
}
const closeNewCalculation = () => {
  showCreateNewCalculation = false
  calculationForm.value.reset()
  newCalculation = {}
}
const loadCalculations = async (creditor: any) => {
  const { id } = creditor
  loading = true
  try {
    creditor.calculations = await calculationService.getCalculations(id)
  }
  catch (error) {
    printError('ERROR ON LOAD CALCULATIONS OF CREDITOR:', error)
  }
  finally {
    loading = false
  }
}

// Options Helpers list
let incidents: any[] = $ref([])
const addIncident = async (incidentNumber: string) => {
  try {
    const result: any = await calculationService.newIncident(incidentNumber)
    const { id, number } = result
    return { id, number, description: number }
  }
  catch (error) {
    printError('ERROR ON LOAD INCIDENSTS:', error)
  }
}
const loadIncidents = async () => {
  try {
    incidents = await calculationService.getIncidents()
  }
  catch (error) {
    printError('ERROR ON LOAD INCIDENSTS:', error)
  }
}
const options = $ref({
  users: [],
  judges: [],
  lawyers: [],
  courts: [],
  regions: [],
})
const loadOptions = async () => {
  options.users = await usersService.getUsers()
  options.judges = await projectService.getJudges()
  options.lawyers = await projectService.getLawyers()
  options.courts = await projectService.getCourts()
  options.regions = await projectService.getRegions()
}

onMounted(() => {
  loadIncidents()
  loadProject()
  loadOptions()
})
</script>

<template>
  <Page
    menu-label="Informações Principais"
    :loading="loading"
    :links="[{ label: 'Projetos', url: '/projetos' }, { label: project.description }]"
  >
    <template #menu>
      <ProjectDescription :project="project" />
    </template>

    <Header :title="`Projeto ${project.description || ''}`">
      <Btn
        label="Participantes"
        icon="i-carbon-events"
        outlined
        @click="showParticipants = true"
      />
      <Btn
        label="Editar"
        icon="i-carbon-edit"
        :disabled="!project.id"
        @click="showEditingProject = true"
      />
    </Header>

    <div class="grid grid-cols-3 grid-rows-2 gap-6 mb-8">
      <GraphGauge
        :values="[]"
        title="Quantidade de Cálculos por Status"
        hint="Esse gráfico apresenta a quantidade de Cálculos para cada status."
        class="row-span-2"
      />
      <GraphCard
        title="Quantidade Total de Credores"
        hint="O Número total dos Credores deste Projeto."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          0
        </div>
      </GraphCard>
      <GraphCard
        title="Valor Total dos Credores"
        hint="Somatório dos Cálculos aprovados de todos os Credores."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          R$ 0 mil
        </div>
      </GraphCard>
      <ProgressList
        :values="[]"
        title="Quantidade de Cálculos por Classe"
        hint="Classes na Recuperação Judicial:\n  • Classe I - Créditos Trabalhistas\n  • Classe II - Créditos com Garantia Real\n  • Classe III - Créditos Quirográficos\n  • Classe IV - Créditos enquadrados como Microempresa ou Empresa de pequeno porte."
      />
      <ProgressList
        :values="[]"
        title="Valores dos Cálculos por Classe (mil R$)"
        hint="Classes na Recuperação Judicial:\n  • Classe I - Créditos Trabalhistas\n  • Classe II - Créditos com Garantia Real\n  • Classe III - Créditos Quirográficos\n  • Classe IV - Créditos enquadrados como Microempresa ou Empresa de pequeno porte."
      />
    </div>

    <Header title="Cálculos">
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Cálculos"
          @click="loadProject"
        />
      </template>
      <Btn
        label="Exportar Cálculos Válidos"
        icon="i-carbon-document-export"
        disabled
        outlined
      />
      <Btn
        label="Credores"
        @click="router.push({ path: `/projeto/${attrs.projectId}/credores` })"
      />
    </Header>

    <TabFilter
      v-model="tab"
      v-model:search="filterBy"
      :items="tabFilters"
    />

    <div v-if="filteredRecoverings.length > 0" class="grid gap-3">
      <Accordion
        v-for="recovering in filteredRecoverings"
        :key="recovering.id"
        :title="recovering.entity.name"
        :subtitle="formatLegalNumber(recovering.entity.legalNumber)"
        class="w-[min(calc(100vw_-_106px),100%)_!important]"
      >
        <template #header-left>
          <IconHint
            icon="i-carbon-enterprise"
            hint="Este ícone indica que este\nitem é uma Recuperanda!"
            dark
            class="self-center"
          />
        </template>
        <template #header-right>
          <div class="flex-1 flex gap-2 justify-end items-center pl-4 pr-4">
            <div class="font-bold flex no-wrap items-center gap-2 text-lg">
              Total: R$ 0
              <Hint value="Total dos Cálculos Aprovados." />
            </div>
          </div>
        </template>
        <div v-if="recovering.creditors.length > 0">
          <Accordion
            v-for="(creditor, index) in recovering.creditors"
            :key="creditor.id"
            v-model="creditor.isOpen"
            :title="creditor.entity.name"
            :subtitle="formatLegalNumber(creditor.entity.legalNumber)"
            class="border-x-0 border-b-0 rounded-0"
            summary-class="pl-8"
            :class="{ 'border-t-0': index === 0 }"
            @open="loadCalculations(creditor)"
          >
            <template #header-left>
              <IconHint
                icon="i-carbon-identification"
                hint="Este ícone indica que este\nitem é um Credor!"
                class="self-center"
              />
            </template>
            <template #header-right>
              <div class="flex-1 flex items-center">
                <Btn
                  label="Novo Cálculo"
                  icon="i-carbon-add-filled"
                  transparent
                  @click.stop="openNewCalculation(creditor)"
                />
              </div>
            </template>
            <CalculationTable
              v-model="creditor.calculations"
              @row-click="(row) => openCalculation(creditor.id, row.id)"
            />
          </Accordion>
        </div>
        <div v-else class="p-6 text-center">
          Nenhum Credor cadastrado para essa Recuperanda
        </div>
      </Accordion>
    </div>
    <div v-else class="text-lg text-center pt-5">
      Nenhuma Recuperanda nessa listagem...
    </div>

    <template #out>
      <UpdateProject
        v-model="showEditingProject"
        v-model:project="project"
        v-model:options="options"
        @success="loadProject"
      />
      <Modal
        v-model="showParticipants"
        title="Participantes"
        hint="Esses são os Participantes e suas funções dentro do Projeto."
      >
        <div class="p-8 pt-4">
          <div
            v-for="(group, key) in project.participants"
            :key="key"
            class="mb-4"
          >
            <div class="font-bold mb-3">
              {{ key }}:
            </div>
            <div class="flex gap-2">
              <UserTag
                v-for="user in group" :key="user.id"
                :model-value="user"
              />
            </div>
          </div>
        </div>
      </Modal>
      <Modal
        v-model="showCreateNewCalculation"
        title="Criar um Novo Cálculo"
        hint="Para criar um cálculo é preciso escolher um incidente."
        modal-class="max-w-120"
        @close="closeNewCalculation"
      >
        <QForm
          ref="calculationForm"
          @submit="createNewCalculation"
        >
          <div class="px-4">
            <InputSelect
              v-model="newCalculation.incidentId"
              v-model:options="incidents"
              label="Número de Incidente"
              :to-add="addIncident"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :disable="loading"
            />
            <label class="flex gap-4 items-center mb-4">
              <div class="">Fase do Cálculo</div>
              <BtnToggle
                v-model="newCalculation.isAdm"
                class="bg--base flex-1"
                :items="[
                  { label: 'Administrativa', value: true },
                  { label: 'Judiciária', value: false },
                ]"
              />
            </label>
          </div>
          <div class="flex justify-end p4 border-t-1 border-black/12">
            <Btn
              label="Criar Cálculo"
              type="submit"
              loading-label="Criando Novo Cálculo..."
              :loading="loading"
            />
          </div>
        </QForm>
      </Modal>
    </template>
  </Page>
</template>

<route lang="yaml">
meta:
  authentication: true
</route>

<style>
.calculation-table thead {
  background-color: #3331;
  font-weight: 600;
}
</style>
