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
  .reduce((acc: any, project) => {
    const { legalManager, legalPartner, financialManager, financialPartner, calculationManager } = project
    const responsibles = [legalManager, legalPartner, financialManager, financialPartner, calculationManager]
      .map((responsible: any) => responsible?.fullName)
    responsibles.forEach((responsible) => {
      if (!responsible)
        return acc
      if (!acc[responsible])
        acc[responsible] = 0
      acc[responsible]++
    })
    return acc
  }, {}))
  .sort(([labelA], [labelB]) => (labelA < labelB) ? -1 : 1)
  .map(([label, count = 0]) => ({ label, count: Number(count) })))

const usageData: any[] = []

const loadProjects = async () => {
  loading = true
  try {
    const projectResult = await projectService.getProjects()

    const recoveringResult = await recoveringService.getRecoverings()
    const getRecovering = (project: string) => recoveringResult
      .find(({ projectId }: any) => projectId === project)

    projects = projectResult?.map((project: any) => ({
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
    name: 'responsibles',
    field: 'responsibles',
    label: 'Responsáveis',
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
  <Page
    :links="[{ label: 'Projetos' }]"
  >
    <Header title="Projetos">
      <Btn
        label="Novo Projeto"
        @click="showNewProject = true"
      />
    </Header>

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

    <Header :title="`Projetos (${projectsCount})`">
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Projetos"
          @click="loadProjects"
        />
      </template>
      <SearchFilter v-model="filterBy" />
    </Header>

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
      <template #body-cell-responsibles="props">
        <QTd :props="props">
          <div class="flex">
            <div class="flex items-center no-wrap rounded-full px-3 py-1 border-1 border-gray/20 bg-gray/20 whitespace-nowrap cursor-help">
              {{ props.value.length }} responsáveis
              <QTooltip v-if="props.value.length">
                <div class="grid gap-2 p-2">
                  <div
                    v-for="(item, index) in props.value"
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
          <div class="flex">
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
        @success="showNewProject = false; loadProjects()"
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
