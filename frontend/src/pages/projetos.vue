<script setup lang="ts">
import GraphLine from '../components/common/GraphLine.vue'

const router = useRouter()

const projects = $ref([])
const projectsCount = computed(() => projects.length)

onMounted(async () => {
  try {
    const projectList = await projectService.getProjects()
    const recoveringList = await recoveringService.getRecovering()
    // eslint-disable-next-line no-console
    console.log({ projectList, recoveringList })
  }
  catch (error) {
    console.warn('ERROR LOADING PROJECTS:', error)
  }
})

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
    name: 'processId',
    field: 'process',
    label: 'N° do Processo',
    align: 'left',
    sortable: true,
  },
  {
    name: 'createdAt',
    field: 'created_at',
    label: 'Data de Criação',
    align: 'left',
    sortable: true,
  },
  {
    name: 'responsable',
    field: 'responsable',
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

const gaugeValues: any[] = []
const responsibleList: any[] = []
const usageData: any[] = []
</script>

<template>
  <div class="flex flex-1 justify-center">
    <div class="px-8 py-8 max-w-400 flex-1">
      <button
        class="group mb-8 flex gap-1 items-center uppercase font-semibold hover:text--secondary transition duration-300 ease-in-out"
        @click="router.push({ path: '/' })"
      >
        <div class="i-carbon-chevron-left group-hover:-translate-x-1 transition duration-300 ease-in-out" />
        Voltar
      </button>

      <div class="mb-8 flex justify-between">
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
          hint="Esse"
        />
        <ProgressList
          :values="responsibleList"
          title="Projetos x Responsável"
          hint="Esse gráfico apresenta o número de Projetos por Responsável."
        />
      </div>

      <div class="flex justify-between mb-8">
        <h2 class="font-bold text-3xl">
          Projetos ({{ projectsCount }})
        </h2>
        <div>
          <label class="relative">
            <span class="mr-4">Buscar</span>
            <input type="text" class="border-1 border-black/12 py-1 pl-1 pr-8 rounded-.5">
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
        row-key="name"
        flat
        bordered
      />
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
