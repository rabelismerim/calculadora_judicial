<script setup lang="ts">
const router = useRouter()

let loading = $ref(false)
const showNewProject = $ref(false)
const filterBy = $ref('')

let projects = $ref([])
const projectsCount = computed(() => projects.length)

const statusColors: any = {
  p: '#c4d600', // Em Preparação
  e: '#c4d600', // Em Preparação
  c: '#86bc25', // Concluído
  a: '#007cb0', // Em Andamento
  f: '#cccccc', // Cancelado
}
const gaugeValues = computed(() => Object.entries(projects
  .reduce((acc: any, { statusDisplay, status }: any) => {
    if (!acc[statusDisplay]) {
      acc[statusDisplay] = {
        count: 0,
        color: statusColors[status.toLowerCase()],
      }
    }
    acc[statusDisplay].count += 1
    return acc
  }, {}))
  .map(([label, content]) => {
    const { count, color }: any = content
    return { label, count, color }
  }))

const responsibleList = computed(() => Object.entries(projects
  .reduce((acc: any, { responsible }) => {
    if (!acc[responsible])
      acc[responsible] = 0
    acc[responsible]++
    return acc
  }, {}))
  .map(([label, count = 0]) => ({ label, count: Number(count) })))

const usageData: any[] = []

const loadProjects = async () => {
  loading = true
  try {
    const projectResult = await projectService.getProjects()

    const recoveringResult = await recoveringService.getRecoverings()
    const getRecovering = (project: string) => recoveringResult
      .find(({ projectId }: any) => projectId === project)

    projects = projectResult.map((project: any) => ({
      ...getRecovering(project.id),
      ...project,
    }))
  }
  catch (error) {
    printError('ERROR ON LOAD PROJECTS:', error)
  }
  finally {
    loading = false
  }
}

const openProject = (_: Event, { id }: any) => router.push(`/projeto/${id}`)

onMounted(() => loadProjects())

const columns = [
  {
    name: 'name',
    field: 'description',
    required: true,
    label: 'Projeto',
    align: 'left',
    sortable: true,
  },
  {
    name: 'process',
    field: 'processNumber',
    label: 'N° do Processo',
    align: 'left',
    sortable: true,
  },
  {
    name: 'createdAt',
    field: 'createdAt',
    label: 'Data de Criação',
    align: 'left',
    sortable: true,
    format: (value) => {
      const [month, day, year] = value.split('/')
      return `${day}/${month}/${year}`
    },
  },
  {
    name: 'responsible',
    field: 'responsible',
    label: 'Responsável',
    align: 'left',
    sortable: true,
  },
  {
    name: 'company',
    field: 'company',
    label: 'Recuperanda(s)',
    align: 'left',
    sortable: true,
  },
  {
    name: 'fase',
    field: 'fase',
    label: 'Fase',
    align: 'left',
    sortable: true,
  },
  {
    name: 'status',
    field: 'statusDisplay',
    label: 'Status',
    align: 'left',
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
  <div class="flex flex-1 justify-center">
    <div class="px-8 py-8 max-w-[min(1600px,100vw)] flex-1">
      <button
        class="group mb-8 flex gap-1 items-center uppercase font-semibold hover:text--secondary tween"
        @click="router.push({ path: '/' })"
      >
        <div class="i-carbon-chevron-left group-hover:-translate-x-1 tween" />
        Voltar
      </button>

      <div class="mb-8 flex justify-between gap-4">
        <h1 class="font-bold text-4xl">
          Projetos
        </h1>
        <Btn
          label="Novo Projeto"
          @click="showNewProject = true"
        />
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 xl:grid-cols-12 gap-6 mb-8">
        <GraphGauge
          :values="gaugeValues"
          title="Status dos projetos"
          hint="Esse gráfico apresenta a quantidade de cálculo total de todos os projetos pelo tempo."
          class="md:col-span-2 xl:col-span-3"
        />
        <GraphGauge
          :values="[]"
          title="Quantidade de Cálculos por Fase"
          hint="Esse gráfico apresenta a quantidade de cálculos em cada fase."
          empty-label="Sem cálculos disponíveis"
          class="md:col-span-2 xl:col-span-3"
        />
        <GraphLine
          :values="usageData"
          title="Uso da Ferramenta x Tempo"
          hint="Esse gráfico mostra o uso da ferramenta no último mês."
          class="sm:col-span-2 xl-col-span-3"
        />
        <ProgressList
          :values="responsibleList"
          title="Projetos x Responsável"
          hint="Esse gráfico apresenta o número de Projetos por Responsável."
          class="sm:col-span-2 xl:col-span-3"
        />
      </div>

      <div class="flex justify-between mb-8 gap-4">
        <div class="flex no-wrap gap-2 items-center">
          <h2 class="font-bold text-3xl">
            Projetos ({{ projectsCount }})
          </h2>
          <ReloadBtn
            hint="Recarregar a Lista de Projetos"
            @click="loadProjects"
          />
        </div>
        <SearchFilter v-model="filterBy" />
      </div>

      <QTable
        class="my-header-table"
        :rows="projects"
        :columns="columns"
        :loading="loading"
        :filter="filterBy"
        row-key="id"
        flat
        bordered
        @row-click="openProject"
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
        <template #body-cell-status="props">
          <QTd :props="props">
            <div class="flex">
              <StatusTag
                :label="props.value"
                :color="statusColors[props.row.status.toLowerCase()]"
              />
            </div>
          </QTd>
        </template>
      </QTable>
    </div>
  </div>
  <newProject
    v-model="showNewProject"
    @success="showNewProject = false; loadProjects()"
  />
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
