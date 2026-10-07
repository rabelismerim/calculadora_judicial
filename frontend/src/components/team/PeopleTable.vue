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

const { hasPermissions } = $user
const showUserModal = $ref(false)
const modalUser = $ref({ fullName: '' })
const editUser = (evt: Event, user: any) => {
  if (hasPermissions('can_authorize_users'))
    emit('editingUser', user)
}

const goTo = (project: any) => {
  router.push({ path: `/projeto/${project.id}` })
}

const filteredItems = computed(() => {
  if (props.tab === 'all')
    return props.items
  return props.items
    .filter(({ groups }: any) => groups
      .some((group: any) => {
        const groupName = group.name?.toLowerCase() || ''
        if (props.tab !== 'gestor')
          return groupName?.includes(props.tab)
        return ['gestor', 'sócio'].some(item => groupName.includes(item))
      }))
})

const filters = [
  { label: 'Todos', value: 'all' },
  { label: 'Administrador', value: 'admin' },
  { label: 'Gestor', value: 'gestor' },
  { label: 'Consultor', value: 'consultor' },
]
const statusColors: any = {
  true: '#2563eb', // Ativo
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
  classes?: string
}
const columns = [
  {
    name: 'name',
    field: 'fullName',
    label: 'Usuário',
    required: true,
    align: 'left',
    classes: 'w-60',
    sortable: true,
  },
  {
    name: 'email',
    field: 'email',
    label: 'Email',
    align: 'left',
    classes: 'w-25',
    sortable: true,
  },
  {
    name: 'permission',
    field: 'groups',
    label: 'Permissão',
    align: 'left',
    format: (value: any[]) => value.map(({ name }: any) => name).join(' '),
    classes: 'w-25 max-w-100 overflow-hidden text-ellipsis',
    sortable: true,
  },
  {
    name: 'role',
    field: 'roleDisplay',
    label: 'Cargo',
    align: 'left',
    format: (value: string) => value ?? '-',
    classes: 'w-25',
    sortable: true,
  },
  {
    name: 'status',
    field: 'isActive',
    label: 'Ativo',
    align: 'right',
    classes: 'w-25',
    sortable: true,
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
        <div class="flex justify-end">
          <StatusTag
            :label="props.row?.statusDisplay"
            :color="statusColors[props.value]"
          />
        </div>
      </QTd>
    </template>
  </QTable>
  <TeamProjectsModal
    v-model="showUserModal"
    :user="modalUser"
  />
</template>
