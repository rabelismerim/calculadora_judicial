<script setup lang="ts">
const router = useRouter()
const { updateProjectList, hasPermissions } = $user

let loading = $ref(false)
let showNewProject = $ref(false)
let pagination = $ref({
  sortBy: 'description',
  descending: false,
  page: 1,
  rowsPerPage: 5,
  rowsNumber: 5,
  filterBy: '',
  filterColumn: 'description',
})

let projects = $ref([])

const statusColors: any = {
  p: '#c4d600', // Em Preparação
  e: '#c4d600', // Em Preparação
  c: '#2563eb', // Concluído
  a: '#007cb0', // Em Andamento
  f: '#cccccc', // Cancelado
}

let bigNumbers: any = $ref({})
const loadBigNumbers = async () => {
  try {
    bigNumbers = await projectService.getDashboardBigNumbers()
  }
  catch (error) {
    printError('ERROR ON LOADING PROJECT BIG NUMBERS:', error)
  }
}
async function loadProjects(props: any = {}) {
  const localPagination = {
    ...pagination,
    ...props.pagination,
  }
  loading = true
  try {
    loadBigNumbers()
    const { items, count: rowsNumber } = await projectService.getProjects(localPagination)
    projects = items
    pagination = {
      ...localPagination,
      rowsNumber,
    }
  }
  catch (error) {
    printError('ERROR ON LOAD PROJECTS:', error)
  }
  finally {
    loading = false
  }
}

const redirectToProject = (_: any, row: any) => {
  router.push(`/projeto/${row.id}`)
}

const onProjectCreated = async () => {
  loading = true
  showNewProject = false
  await updateProjectList()
  await loadProjects()
  loading = false
}

onMounted(() => {
  loadProjects()
})

const columns = [
  {
    name: 'description',
    field: 'description',
    required: true,
    label: 'Projeto',
    align: 'left',
    sortable: true,
  },
  {
    name: 'process_number',
    field: 'processNumber',
    label: 'N° do Processo',
    align: 'left',
    sortable: true,
  },
  {
    name: 'created_at',
    field: 'createdAt',
    label: 'Data de Criação',
    align: 'left',
    sortable: true,
    sortOrder: 'da',
    format: formatDateFromBackend,
  },
  {
    name: 'responsibles',
    field: 'responsibles',
    label: 'Responsáveis',
    align: 'left',
  },
  {
    name: 'is_adm',
    field: 'isAdm',
    label: 'Fase',
    align: 'left',
    format: value => value ? 'Administrativa' : 'Judicial',
    sortable: true,
  },
  {
    name: 'status',
    field: 'statusDisplay',
    label: 'Status',
    align: 'right',
    sortable: true,
  },
] as {
  name: string
  label: string
  field: string
  required?: boolean
  align?: 'left' | 'right' | 'center'
  sortable?: boolean
  format?: (val: any, row: any) => any
}[]
</script>

<template>
  <Page
    :links="[{ label: 'Projetos' }]"
  >
    <Header title="Projetos">
      <Btn
        v-if="hasPermissions('add_project')"
        label="Novo Projeto"
        @click="showNewProject = true"
      />
    </Header>

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 xl:grid-cols-12 gap-6 mb-8">
      <GraphGauge
        :values="bigNumbers.countStatus"
        title="Status dos projetos"
        hint="Esse gráfico apresenta a quantidade de cálculo total de todos os projetos pelo tempo."
        class="md:col-span-2 xl:col-span-3"
      />
      <GraphGauge
        :values="bigNumbers.byPhase"
        title="Quantidade de Cálculos por Fase"
        hint="Esse gráfico apresenta a quantidade de cálculos em cada fase."
        empty-label="Sem cálculos disponíveis"
        class="md:col-span-2 xl:col-span-3"
      />
      <ProgressList
        :values="bigNumbers.countUsers"
        title="Projetos x Responsável"
        hint="Esse gráfico apresenta o número de Projetos por Responsável."
        class="sm:col-span-2 xl:col-span-3"
      />
      <GraphLine
        :values="bigNumbers.rangeDays"
        title="Uso da Ferramenta x Tempo"
        hint="Esse gráfico mostra o uso da ferramenta no último mês."
        class="sm:col-span-2 xl-col-span-3"
      />
    </div>

    <Header title="Projetos" :tag="pagination.rowsNumber ?? 0">
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Projetos"
          @click="loadProjects"
        />
      </template>
      <SearchFilter
        v-model:search="pagination.filterBy"
        v-model:field="pagination.filterColumn"
        :options="{
          description: 'Nome do Projeto',
          process_number: 'N° do Processo',
          status: 'Status',
        }"
      />
    </Header>

    <QTable
      v-model:pagination="pagination"
      class="my-header-table"
      :rows="projects"
      :columns="columns"
      :loading="loading"
      :filter="pagination.filterBy"
      :rows-per-page-options="[5, 10, 15, 20, 25]"
      row-key="id"
      flat
      bordered
      @row-click="redirectToProject"
      @request="loadProjects"
    >
      <template #body-cell-name="props">
        <QTd :props="props">
          <div class="flex no-wrap items-center gap-3 font-bold">
            <div class="h-10 w-10 bg-gray-2 rounded-.5 flex justify-center items-center text-[16px]">
              {{ getInitials(props.value) }}
            </div>
            <div class="text-[14px]">
              {{ props.value }}
            </div>
          </div>
        </QTd>
      </template>
      <template #body-cell-responsibles="props">
        <QTd :props="props">
          <div class="flex">
            <div class="flex items-center no-wrap rounded-full px-3 py-1 border-1 border-gray/20 bg-gray/20 whitespace-nowrap cursor-help">
              {{ props.value.length }} responsáveis
              <QTooltip v-if="props.value.length">
                <div class="grid gap-2 p-2">
                  <div
                    v-for="(item, index) in props.value as any[]"
                    :key="index"
                    class="flex no-wrap items-center justify-between gap-2"
                  >
                    {{ item.role }}:
                    <UserTag :model-value="item.user" />
                  </div>
                </div>
              </QTooltip>
            </div>
          </div>
        </QTd>
      </template>
      <template #body-cell-status="props">
        <QTd :props="props">
          <div class="flex justify-end">
            <StatusTag
              :label="props.value"
              :color="statusColors[props.row.status.toLowerCase()]"
            />
          </div>
        </QTd>
      </template>
    </QTable>

    <template #out>
      <newProject
        v-model="showNewProject"
        @success="onProjectCreated"
      />
    </template>
  </Page>
</template>

<style lang="scss">
.my-header-table {
  border-radius: 2px;
}
</style>

<route lang="yaml">
meta:
  authenticated: true
</route>
