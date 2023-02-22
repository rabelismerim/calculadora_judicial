<script setup lang="ts">
const router = useRouter()

const projects = $ref([])
const projectsCount = computed(() => projects.length)

const columns = [
  {
    name: 'name',
    filed: 'name',
    required: true,
    label: 'Projeto',
    align: 'left',
    sortable: true,
  },
  {
    name: 'processId',
    filed: 'process',
    label: 'N° do Processo',
    align: 'left',
    sortable: true,
  },
  {
    name: 'createdAt',
    filed: 'created_at',
    label: 'Data de Criação',
    align: 'left',
    sortable: true,
  },
  {
    name: 'responsable',
    filed: 'responsable',
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
]
</script>

<template>
  <div class="flex flex-1 justify-center bg--base">
    <div class="px-8 py-8 max-w-400 flex-1">
      <button
        class="mb-8 flex gap-1 items-center uppercase font-semibold hover:underline hover:text--secondary transition duration-300 ease-in-out"
        @click="router.push('/')"
      >
        <div class="i-carbon-chevron-left" />
        Voltar
      </button>

      <div class="mb-8 flex justify-between">
        <h1 class="font-bold text-4xl">
          Home
        </h1>
        <Btn disabled>
          Novo Projeto
        </Btn>
      </div>

      <div class="grid grid-cols-3 gap-6 ">
        <div class="bg-white p-4 border-1 border-black/12 rounded-.5 aspect-video">
          teste
        </div>
        <div class="bg-white p-4 border-1 border-black/12 rounded-.5 aspect-video">
          teste
        </div>
        <div class="bg-white p-4 border-1 border-black/12 rounded-.5 aspect-video">
          teste
        </div>
      </div>

      <div class="flex justify-between">
        <h2 class="font-bold text-3xl">
          Projetos ({{ projectsCount }})
        </h2>
        <div>
          <label class="relative">
            <spn class="mr-4">Buscar</spn>
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
