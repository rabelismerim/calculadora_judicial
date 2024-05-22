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
    open?: boolean
    loading?: boolean
    pagination?: any
  }[]
  engagement: {
    numbers: any[]
  }
  participants: {
    user: any
  }[]
  [key: string]: any
}

const nullPagination = {
  sortBy: 'name',
  descending: false,
  page: 1,
  rowsPerPage: 5,
  rowsNumber: 5,
  filterBy: '',
  filterColumn: 'name',
}

let loading = $ref(false)
const showParticipants = $ref(false)
let project = $ref({} as Project)
const showEditingProject = $ref(false)

let bigNumbers: any = $ref({})
const loadBigNumbers = async () => {
  try {
    bigNumbers = await projectService.getProjectBigNumbers(attrs.projectId)
  }
  catch (error) {
    printError('ERROR ON LOADING PROJECT BIG NUMBERS:', error)
  }
}
const loadProject = async () => {
  loading = true
  try {
    loadBigNumbers()
    const result = await projectService.getProject(attrs.projectId)
    project = {
      ...result,
      recoverings: result?.recoverings?.map((recovering: any) => ({
        ...recovering,
        open: false,
        loading: false,
        pagination: { ...nullPagination },
      })),
    }
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

let expandedCalculation = $ref('')
const loadCalculations = async (props: any) => {
  const { row: { id } = {} as any } = props
  if (expandedCalculation === id) {
    expandedCalculation = ''
    return
  }
  expandedCalculation = id
  loading = true
  try {
    const noticeAJResult = await creditorsService.getNoticeAJCreditor(id)
    const noticeRJResult = await creditorsService.getNoticeAJRecovering(id)
    const noticesAJ = noticeAJResult
      ?.map((notice: any) => ({
        number: 'AJ',
        incident: { number: 'Edital AJ' },
        isAdm: false,
        classes: notice?.classes ?? {},
        coins: notice?.coins ?? {},
        createdAt: notice.createdAt || '-',
        stepDisplay: 'Edital',
      }))

    const noticesRJ = noticeRJResult
      ?.map((noticeRecovering: any) => ({
        number: 'RJ',
        incident: { number: 'Edital RJ' },
        isAdm: true,
        classes: noticeRecovering?.classes ?? {},
        coins: noticeRecovering?.coins ?? {},
        createdAt: noticeRecovering.createdAt || '-',
        stepDisplay: 'Edital',
      }))

    const calculationsResult = await calculationService.getCalculations(id)
    props.row.calculations = [
      ...noticesRJ,
      ...noticesAJ,
      ...(calculationsResult || []),
    ]
  }
  catch (error) {
    printError('ERROR ON LOAD CALCULATIONS OF CREDITOR:', error)
  }
  finally {
    loading = false
  }
}

const creditorColumns = [
  {
    name: 'entity__name',
    field: 'entity',
    label: 'Credor',
    align: 'left',
    classes: 'w-25',
    sortable: true,
    format: value => value?.name ?? '-',
  },
  {
    name: 'entity__legal_number',
    field: 'entity',
    label: 'CPF/CNPJ',
    align: 'left',
    classes: 'w-25',
    sortable: true,
    format: value => formatLegalNumber(value?.legalNumber),
  },
  {
    name: 'person_type',
    field: 'personType',
    label: 'Tipo',
    align: 'left',
    classes: 'w-25',
    sortable: true,
    format: value => value ?? '-',
  },
  {
    name: 'action',
    field: 'action',
    label: 'Ação',
    classes: 'flex justify-end min-h-14 gap-3',
    headerClasses: 'pr-24!',
  },
] as {
  name: string
  label: string
  field: string
  classes?: string
  headerClasses?: string
  required?: boolean
  align?: 'left' | 'right' | 'center'
  sortable?: boolean
  format?: (val: any, row: any) => any
}[]

const loadCreditors = async (recovering: any, props: any = {}) => {
  recovering.loading = true
  const localPagination = {
    ...nullPagination,
    ...recovering.pagination,
    ...props.pagination,
  }
  try {
    const { items, count: rowsNumber } = await creditorsService.getCreditorsByLegalNumber(attrs.projectId, recovering?.entity?.legalNumber, localPagination)
    recovering.creditors = items

    for (const creditor of recovering.creditors)
      creditor.total = await projectService.getCreditorBigNumbers(creditor.id)

    recovering.pagination = {
      ...localPagination,
      rowsNumber,
    }
  }
  catch (error) {
    printError(`ERROR ON LOADING RECOVERING ${formatLegalNumber(recovering.entity?.legalNumber)}`, error)
  }
  finally {
    recovering.loading = false
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

onMounted(async () => {
  login()
  loadOptions()
  loadProject()
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
    <div v-if="project?.recoverings?.length > 0" class="flex flex-col gap-3">
      <Accordion
        v-for="recovering in project?.recoverings ?? []"
        :key="recovering.id"
        v-model="recovering.open"
        :title="recovering.entity?.name"
        :subtitle="formatLegalNumber(recovering.entity.legalNumber)"
        class="accordion w-[min(1600px,100%)_!important]"
        @open="loadCreditors(recovering)"
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
            <!-- <div class="font-bold flex no-wrap items-center gap-2 text-lg">
              Total: R$ {{ formatNumber(recovering?.total || 0, 2) }}
              <Hint value="Total dos Cálculos Aprovados." />
            </div> -->
            <SearchFilter
              v-if="recovering.open"
              v-model:search="recovering.pagination.filterBy"
              v-model:field="recovering.pagination.filterColumn"
              :options="{
                name: 'Nome do Credor',
                cpf_cnpj: 'CPF/CNPJ do Credor',
              }"
              @update:search="loadCreditors(recovering)"
            />
          </div>
        </template>

        <QTable
          v-model:pagination="recovering.pagination"
          :columns="creditorColumns"
          :rows="recovering.creditors"
          :rows-per-page-options="[5, 10, 15, 20, 25]"
          no-data-label="Nenhum Credor cadastrado para essa Recuperanda"
          row-key="id"
          flat
          @request="props => loadCreditors(recovering, props)"
        >
          <template #header="props">
            <QTr :props="props">
              <QTh auto-width />
              <QTh
                v-for="col in props.cols"
                :key="col.name"
                :props="props"
              >
                {{ col.label }}
              </QTh>
            </QTr>
          </template>
          <template #body="props">
            <QTr
              :props="props"
              class="cursor-pointer"
              @click="loadCalculations(props)"
            >
              <QTd auto-width>
                <div
                  :class="{ 'rotate-180': props.row?.id === expandedCalculation }"
                  class="group h-8 w-8 rounded-8 text--secondary text-5 flex justify-center items-center hover:bg--secondary/20 tween-600"
                >
                  <div class="i-carbon-chevron-down" />
                </div>
              </QTd>
              <QTd
                v-for="col in props.cols"
                :key="col.name"
                :props="props"
              >
                <Btn
                  v-if="col.name === 'action'"
                  label="Novo Cálculo"
                  icon="i-carbon-add-filled"
                  transparent
                  @click.stop="openNewCalcultation(props.row?.id)"
                />
                <span v-else>{{ col.value }}</span>
              </QTd>
            </QTr>
            <QTr v-show="expandedCalculation === props.row?.id" :props="props">
              <QTd colspan="100%" class="p-0!">
                <CalculationTable
                  v-model="props.row.calculations"
                  v-model:validation="props.row.isValidating"
                  :creditor="props.row"
                  @row-click="(row: any) => openCalculation(props.row?.id, row.id)"
                  @validated="loadCalculations(props.row); loadBigNumbers()"
                />
              </QTd>
            </QTr>
          </template>
        </QTable>
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
