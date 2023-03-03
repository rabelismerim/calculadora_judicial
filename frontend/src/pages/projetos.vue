<script setup lang="ts">
const router = useRouter()

let loading = $ref(false)
const filterBy = $ref('')
let projects = $ref([])
const projectsCount = computed(() => projects.length)
const gaugeValues = computed(() => Object.entries(projects
  .reduce((acc: any, { status }) => {
    if (!acc[status])
      acc[status] = 0
    acc[status]++
    return acc
  }, {}))
  .map(([label, count]) => ({ label, count })))

const responsibleList = computed(() => Object.entries(projects
  .reduce((acc: any, { responsible }) => {
    if (!acc[responsible])
      acc[responsible] = 0
    acc[responsible]++
    return acc
  }, {}))
  .map(([label, count]) => ({ label, count })))

const usageData: any[] = []

const loadProjects = async () => {
  loading = true
  try {
    const projectResult = await projectService.getProjects()

    const recoveringResult = await recoveringService.getRecovering()
    const getRecovering = (project: string) => recoveringResult.find(({ projectId }: any) => projectId === project)

    projects = projectResult.map((project: any) => ({
      ...getRecovering(project.id),
      ...project,
    }))
  }
  catch (error) {
    throwError(error)
    console.warn('ERROR LOADING PROJECTS:', error)
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
    field: 'name',
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
    field: 'status',
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

}[]
</script>

<template>
  <div class="flex flex-1 justify-center">
    <div class="px-8 py-8 max-w-[min(1600px,100vw)] flex-1">
      <button
        class="group mb-8 flex gap-1 items-center uppercase font-semibold hover:text--secondary transition duration-300 ease-in-out"
        @click="router.push({ path: '/' })"
      >
        <div class="i-carbon-chevron-left group-hover:-translate-x-1 transition duration-300 ease-in-out" />
        Voltar
      </button>

      <div class="mb-8 flex justify-between gap-4">
        <h1 class="font-bold text-4xl">
          Projetos
        </h1>
        <Btn
          label="Novo Projeto"
          disabled
        />
      </div>

      <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <GraphGauge
          :values="gaugeValues"
          title="Status dos projetos"
          hint="Esse gráfico apresenta a quantidade de cálculo total de todos os projetos pelo tempo."
        />
        <GraphLine
          :values="usageData"
          title="Uso da Ferramenta x Tempo"
          hint="Esse gráfico mostra o uso da ferramenta no último mês."
        />
        <ProgressList
          :values="responsibleList"
          title="Projetos x Responsável"
          hint="Esse gráfico apresenta o número de Projetos por Responsável."
        />
      </div>

      <div class="flex justify-between mb-8 gap-4">
        <div class="flex no-wrap gap-2 items-center">
          <h2 class="font-bold text-3xl">
            Projetos ({{ projectsCount }})
          </h2>
          <button
            class="h-8 w-8 hover:bg-gray/30 rounded-full flex justify-center items-center transition duration-300 ease-in-out"
            @click="loadProjects"
          >
            <div class="i-carbon-restart h-5 w-5" />
          </button>
        </div>
        <div>
          <label class="relative">
            <span class="mr-4">Buscar</span>
            <input
              v-model="filterBy"
              type="text"
              class="border-1 border-black/12 py-1 pl-1 pr-8 rounded-.5"
            >
            <button class="group absolute right-.5 top-50% -translate-y-50% p-1.5 hover:bg--primary transition duration-300 ease-in-out">
              <div class="i-carbon-search group-hover:bg-white transition duration-300 ease-in-out" />
            </button>
          </label>
        </div>
      </div>

      <q-table
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
          <q-td :props="props">
            <div class="flex no-wrap items-center gap-3 font-bold">
              <div class="h-10 w-10 bg-gray-2 rounded-.5 flex justify-center items-center text-[16px]">
                {{ getInitials(props.value) }}
              </div>
              <div class="text-[14px]">
                {{ props.value }}
              </div>
            </div>
          </q-td>
        </template>
        <template #body-cell-status="props">
          <q-td :props="props">
            <div class="flex">
              <div
                class="py-1 pl-3 rounded-full flex no-wrap items-center"
                :class="{
                  'bg-red/20': props.value === 'Em Atraso',
                  'bg-orange/20': props.value === 'Em Preparação',
                  'bg-blue/20': props.value === 'Em Andamento',
                  'bg-green/20': props.value === 'Concluído',
                }"
              >
                <div class="flex-1">
                  {{ props.value }}
                </div>
                <div
                  class="h-4 w-4 bg-red rounded-full mr-2 ml-1.5"
                  :class="{
                    'bg-red': props.value === 'Em Atraso',
                    'bg-orange': props.value === 'Em Preparação',
                    'bg-blue': props.value === 'Em Andamento',
                    'bg-green': props.value === 'Concluído',
                  }"
                />
              </div>
            </div>
          </q-td>
        </template>
      </q-table>
    </div>
  </div>
</template>

<style lang="scss">
.my-header-table {
  border-radius: 2px;
}
</style>

<route lang="yaml">
meta:
  authentication: true
</route>
