<script setup lang='ts'>
const props = withDefaults(defineProps<{
  tab: string
  filter: string
  items: any[]
  loading?: boolean
}>(), {

})

const emit = defineEmits(['update:tab', 'update:filter', 'editingUser'])

const router = useRouter()

const { hasProject, user } = $user
const showUserModal = $ref(false)
const modalUser = $ref({ fullName: '' })
const editUser = (evt: Event, user: any) => {
  emit('editingUser', user)
}

const canGoTo = (project: any) => hasProject(project.id)
const goTo = (project: any) => {
  if (!canGoTo(project))
    return
  router.push({ path: `/projeto/${project.id}` })
}

const filteredItems = computed(() => {
  if (props.tab === 'all')
    return props.items
  return props.items
    .filter(({ status }) => status?.toLowerCase() === props.tab)
})

const filters = [
  { label: 'Todos', value: 'all' },
  { label: 'Administrador', value: 'd' },
  { label: 'Gestor', value: 'c' },
  { label: 'Consultor', value: 'p' },
]
const statusColors: any = {
  true: '#86bc25', // Ativo
  false: '#cccccc', // Inativo
}

interface TableColumn {
  name: string
  label: string
  field: string
  required?: boolean
  align?: 'left' | 'right' | 'center'
  sortable?: boolean
  style?: string
}
const columns = [
  {
    name: 'name',
    field: 'fullName',
    label: 'Usuário',
    required: true,
    align: 'left',
    style: 'width: 240px',
    sortable: true,
  },
  {
    name: 'email',
    field: 'email',
    label: 'Email',
    align: 'left',
    style: 'width: 100px',
    sortable: true,
  },
  {
    name: 'permission',
    field: 'groups',
    label: 'Permissão',
    align: 'left',
    format: (value: any[]) => value.map(({ name }: any) => name),
    style: 'width: 100px',
    sortable: true,
  },
  {
    name: 'role',
    field: 'roleDisplay',
    label: 'Cargo',
    align: 'left',
    format: (value: string) => value || '-',
    style: 'width: 100px',
    sortable: true,
  },

  {
    name: 'status',
    field: 'isActive',
    label: 'Ativo',
    align: 'left',
    style: 'width: 100px',
    sortable: true,
  },

  {
    name: 'count',
    field: 'projects',
    label: 'Total',
    align: 'left',
    style: 'width: 100px',
    format: (value: string) => value?.length || 0,
    sortable: true,
  },
  {
    name: 'projects',
    field: 'projects',
    label: 'Projetos',
    sortable: true,
    align: 'center',
  },
] as TableColumn[]
</script>

<template>
  <TabFilter
    :model-value="tab"
    :search="filter"
    :items="filters"
    @update:model-value="(value: any) => emit('update:tab', value)"
    @update:search="(value: any) => emit('update:filter', value)"
  />
  <QTable
    class="my-header-table"
    :rows="filteredItems"
    :columns="columns"
    :loading="loading"
    :filter="filter"
    row-key="id"
    flat
    bordered
    @row-click="editUser"
  >
    <template #body-cell-name="props">
      <QTd :props="props">
        <div class="flex no-wrap items-center gap-3 font-bold py-2">
          <UserPicture :model-value="props.row" class="h-10 w-10 rounded-1 mr-2" />
          <div class="font-medium">
            <div class="text-lg font-bold">
              {{ props.value }}
            </div>
          </div>
        </div>
      </QTd>
    </template>

    <template #body-cell-status="props">
      <QTd :props="props">
        <div class="flex">
          <StatusTag
            :label="props.row?.statusDisplay"
            :color="statusColors[props.value]"
          />
        </div>
      </QTd>
    </template>

    <template #body-cell-projects="props">
      <QTd :props="props">
        <div class="flex justify-end gap-1 no-wrap">
          <div class="flex justify-end gap-1  max-h-7.5 overflow-hidden">
            <div
              v-for="project in props.value as any[]"
              :key="project.id"
              class="rounded-full px-3 py-1 border-1 border--black/10 bg-gray/10 whitespace-nowrap"
              :class="canGoTo(project) ? 'cursor-pointer hover:bg--primary/20 hover:border--primary/50' : 'cursor-not-allowed'"
              @click="goTo(project)"
            >
              {{ project.description }}
            </div>
          </div>
          <div
            v-if="props.value?.length > 0"
            class="flex justify-end"
          >
            <div class="flex items-center rounded-full px-3 py-1 border-1 border--black/12 bg-gray/10 whitespace-nowrap cursor-pointer hover:bg--primary/50 hover:border--primary/12" @click="{ modalUser = props.row; showUserModal = true }">
              Ver Todos
            </div>
          </div>
        </div>
      </QTd>
    </template>
  </QTable>
  <TeamProjectsModal
    v-model="showUserModal"
    :user="modalUser"
  />
</template>
