<script setup lang="ts">
const attrs = useAttrs() as any
const router = useRouter()

const { hasPermissions, login } = $user

interface Project {
  recoverings: {
    id: string
    entity: any
    creditors: any[]
    total?: number
  }[]
  engagement: {
    numbers: any[]
  }
  participants: {
    user: any
  }[]
  [key: string]: any
}

interface Notice {
  id: string
  createdAt: string
  classes: {
    classeDisplay: string
  }
  coins: {
    coinDisplay: string
    value: number
  }
}

const noticesAJ: Ref<Notice[]> = ref([])

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
const newCalculation: any = $ref({
  creditorId: null,
  show: false,
})
const openNewCalcultation = (creditorId: string) => {
  newCalculation.creditorId = creditorId
  newCalculation.show = true
}
const openCalculation = (creditorId: string, calculationId: string) =>
  router.push({ path: `/projeto/${project.id}/credor/${creditorId}/calculo/${calculationId}` })
const loadCalculations = async (creditor: any) => {
  const { id } = creditor
  loading = true
  try {
    const noticeAJResult = await creditorsService.getNoticeAJCreditor(id)
    const noticeRJResult = await creditorsService.getNoticeAJRecovering(id)
    const noticesAJ = noticeAJResult.data?.map((notices: any) => ({
      classeDisplay: notices.classes?.classeDisplay || '-',
      coinDisplay: notices.coins?.coinDisplay || '-',
      value: notices.coins?.value || '-',
      createdAt: notices.createdAt,
    }))
    const noticesRJ = noticeRJResult.data?.map((noticeRecoverings: any) => ({
      classeDisplay: noticeRecoverings.classes?.classeDisplay || '-',
      coinDisplay: noticeRecoverings.coins?.coinDisplay || '-',
      value: noticeRecoverings.coins?.value || '-',
      createdAt: noticeRecoverings.createdAt,
    }))
    const calculationsResult = await calculationService.getCalculations(id)
    creditor.calculations = [
      ...noticesAJ,
      ...noticesRJ,
      ...calculationsResult,
    ]
  }
  catch (error) {
    printError('ERROR ON LOAD CALCULATIONS OF CREDITOR:', error)
  }
  finally {
    loading = false
  }
}

// Options Helpers list
const options: any = $ref({
  users: [],
  judges: [],
  lawyers: [],
  courts: [],
  regions: [],
  ocurrences: [],
})
const loadOptions = async () => {
  options.users = await usersService.getUsers()
  options.judges = await projectService.getJudges()
  options.lawyers = await projectService.getLawyers()
  options.courts = await projectService.getCourts()
  options.regions = await projectService.getRegions()
  const result = await creditorsService.getOptions()
  options.ocurrences = result.occurrenceOptions ?? []
}
let bigNumbers: any = $ref({})
const loadBigNumbers = async () => {
  try {
    bigNumbers = await projectService.getProjectBigNumbers(attrs.projectId)
  }
  catch (error) {
    printError('ERROR ON LOADING PROJECT BIG NUMBERS:', error)
  }
}
const loadTotalValues = async () => {
  try {
    for (const recovering of project?.recoverings) {
      for (const creditor of recovering?.creditors)
        creditor.total = await projectService.getCreditorBigNumbers(creditor.id)
      recovering.total = recovering?.creditors
        .reduce((acc, { total }: any) => acc + total, 0)
    }
  }
  catch (error) {
    printError('ERROR ON LOADING CREDITORS TOTAL:', error)
  }
}

onMounted(async () => {
  login()
  loadBigNumbers()
  loadOptions()
  await loadProject()
  await loadTotalValues()
})
</script>

<template>
  <Page
    ref="page"
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
        :disabled="!project.id || loading"
        @click="showParticipants = true"
      />
      <Btn
        v-if="hasPermissions('change_project')"
        label="Editar"
        icon="i-carbon-edit"
        :disabled="!project.id || loading"
        @click="showEditingProject = true"
      />
    </Header>

    <div class="grid grid-cols-1 sm:grid-cols2 md:grid-cols-2 lg:grid-cols-3 lg:grid-rows-2 gap-6 mb-8">
      <GraphGauge
        :values="bigNumbers?.byStep"
        title="Quantidade de Cálculos por Status"
        hint="Esse gráfico apresenta a quantidade de Cálculos para cada status."
        class="lg:row-span-2"
      />
      <GraphCard
        title="Quantidade Total de Credores"
        hint="O Número total dos Credores deste Projeto."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          {{ bigNumbers?.totalCreditor || 0 }}
        </div>
      </GraphCard>
      <GraphCard
        title="Valor Total dos Credores"
        hint="Somatório dos Cálculos aprovados de todos os Credores."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          R$ {{ formatNumber(bigNumbers?.totalSumCreditors || 0, 2) }}
        </div>
      </GraphCard>
      <ProgressList
        :values="bigNumbers?.classesCalculationsCount"
        title="Quantidade de Cálculos por Classe"
        hint="Classes na Recuperação Judicial:\n  • Classe I - Créditos Trabalhistas\n  • Classe II - Créditos com Garantia Real\n  • Classe III - Créditos Quirográficos\n  • Classe IV - Créditos enquadrados como Microempresa ou Empresa de pequeno porte."
      />
      <ProgressList
        :values="bigNumbers?.classesCalculationsTotal"
        title="Valores dos Cálculos por Classe (mil R$)"
        hint="Classes na Recuperação Judicial:\n  • Classe I - Créditos Trabalhistas\n  • Classe II - Créditos com Garantia Real\n  • Classe III - Créditos Quirográficos\n  • Classe IV - Créditos enquadrados como Microempresa ou Empresa de pequeno porte."
        :value-keys="['hist', 'calc']"
      />
    </div>

    <Header title="Cálculos">
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Cálculos"
          @click="loadProject"
        />
      </template>
      <div>
        <Btn
          label="Exportar Cálculos Válidos"
          icon="i-carbon-document-export"
          disabled
          outlined
        />
        <QTooltip>Funcionalidade não disponível nesta versão.</QTooltip>
      </div>
      <Btn
        label="Credores"
        :disabled="!project.id || loading"
        @click="router.push({ path: `/projeto/${attrs.projectId}/credores` })"
      />
    </Header>

    <div v-if="filteredRecoverings.length > 0" class="flex flex-col gap-3">
      <Accordion
        v-for="recovering in filteredRecoverings"
        :key="recovering.id"
        :title="recovering.entity.name"
        :subtitle="formatLegalNumber(recovering.entity.legalNumber)"
        class="accordion w-[min(1600px,100%)_!important]"
        :notices-a-j="noticesAJ"
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
              Total: R$ {{ formatNumber(recovering?.total || 0, 2) }}
              <Hint value="Total dos Cálculos Aprovados." />
            </div>
          </div>
        </template>
        <div v-if="recovering.creditors.length > 0">
          <Accordion
            v-for="(creditor, index) in recovering.creditors"
            :key="creditor.id"
            v-model="creditor.isOpen"
            :title="`${creditor.entity.name}`"
            :subtitle="`${formatLegalNumber(creditor.entity.legalNumber)}`"
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
              <div class="flex-1 flex items-center justify-between pr-4">
                <Btn
                  label="Novo Cálculo"
                  icon="i-carbon-add-filled"
                  transparent
                  @click.stop="openNewCalcultation(creditor.id)"
                />
                <div class="font-bold flex no-wrap items-center gap-2 text-lg">
                  Total: R$ {{ formatNumber(creditor?.total || 0, 2) }}
                  <Hint value="Total dos Cálculos Aprovados." />
                </div>
              </div>
            </template>
            <CalculationTable
              v-model="creditor.calculations"
              v-model:validation="creditor.isValidating"
              :creditor="creditor"
              :notices-a-j="noticesAJ"
              @row-click="(row: any) => openCalculation(creditor.id, row.id)"
              @validated="loadCalculations(creditor); loadBigNumbers(); loadTotalValues()"
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
            v-for="([key, group]) in project.participants as any[]"
            :key="key"
            class="mb-4"
          >
            <div class="font-bold mb-3">
              {{ key }}:
            </div>
            <div v-if="group?.length > 0" class="flex gap-2">
              <UserTag
                v-for="user in group"
                :key="user.id"
                :model-value="user"
              />
            </div>
            <div v-else>
              Nenhum usuário cadastrado como {{ key }}
            </div>
          </div>
        </div>
      </Modal>
      <SetCalculation
        v-model:open="newCalculation.show"
        :options="options"
        :creditor-id="newCalculation.creditorId"
        :project-id="attrs.projectId"
        @success="(id : string) => openCalculation(newCalculation.creditorId, id)"
      />
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
