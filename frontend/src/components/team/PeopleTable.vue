<script setup lang='ts'>
const props = withDefaults(defineProps<{
  tab: string
  filter: string
  items: any[]
  loading?: boolean
}>(), {

})
const emit = defineEmits(['update:tab', 'update:filter'])

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
    name: 'permission',
    field: 'groups',
    label: 'Permissão',
    align: 'left',
    format: (value: any[]) => value.map(({ name }: any) => name),
    style: 'width: 100px',
    sortable: true,
  },
  {
    name: 'position',
    field: 'position',
    label: 'Cargo',
    align: 'left',
    format: (value: string) => value || '-',
    style: 'width: 100px',
    sortable: true,
  },
  {
    name: 'area',
    field: 'area',
    label: 'Área',
    align: 'left',
    format: (value: string) => value || '-',
    style: 'width: 100px',
    sortable: true,
  },
  {
    name: 'status',
    field: 'isActive',
    label: 'Status',
    align: 'left',
    style: 'width: 100px',
    sortable: true,
  },
  {
    name: 'projects',
    field: 'projects',
    label: 'Projetos',
    align: 'center',
    sortable: true,
    style: 'width: 100px',
  },
] as TableColumn[]
</script>

<template>
  <TabFilter
    :model-value="tab"
    :search="filter"
    :items="filters"
    @update:model-value="value => emit('update:tab', value)"
    @update:search="value => emit('update:filter', value)"
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
  >
    <template #body-cell-name="props">
      <QTd :props="props">
        <div class="flex no-wrap items-center gap-3 font-bold py-2">
          <UserPicture :model-value="props.row" class="h-12 w-12 rounded-1 mr-2" />
          <div class="font-medium">
            <div class="text-lg font-bold">
              {{ props.value }}
            </div>
            <div>
              {{ props.row.email }}
            </div>
          </div>
        </div>
      </QTd>
    </template>

    <template #body-cell-permission="props">
      <QTd :props="props">
        <div class="flex gap-2">
          <div
            v-for="group in props.value"
            :key="group"
            class="rounded-full px-3 py-1 border-1 border--primary/12 bg--primary/50 whitespace-nowrap"
          >
            {{ group }}
          </div>
        </div>
      </QTd>
    </template>

    <template #body-cell-status="props">
      <QTd :props="props">
        <div class="flex">
          <StatusTag
            :label="props.value ? 'Ativo' : 'Inativo'"
            :color="statusColors[props.value]"
          />
        </div>
      </QTd>
    </template>

    <template #body-cell-action="props">
      <QTd :props="props">
        <div class="flex justify-end">
          <Btn
            :label="props.value ? 'Editar' : 'Cadastrar'"
            :outlined="props.value"
          >
            <div class="i-carbon-chevron-right" />
          </Btn>
        </div>
      </QTd>
    </template>
  </QTable>
</template>
