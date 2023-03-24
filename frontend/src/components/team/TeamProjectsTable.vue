<script setup lang='ts'>
const props = withDefaults(defineProps<{
  tab: string
  filter: string
  items: any[]
  loading?: boolean
}>(), {

})
const emit = defineEmits(['update:tab', 'update:filter'])
const router = useRouter()

const statusColors: any = {
  p: '#c4d600', // Em Preparação
  e: '#c4d600', // Em Preparação
  c: '#86bc25', // Concluído
  a: '#007cb0', // Em Andamento
  f: '#cccccc', // Cancelado
}

const filteredItems = computed(() => {
  if (props.tab === 'all')
    return props.items
  return props.items
    .filter(({ status }) => status?.toLowerCase() === props.tab)
})

const filters = [
  { label: 'Todos', value: 'all' },
  { label: 'Em Preparação', value: 'e' },
  { label: 'Em Andamento', value: 'a' },
  { label: 'Concluído', value: 'c' },
  { label: 'Cancelado', value: 'f' },
]

interface TableColumn {
  name: string
  label: string
  field: string
  required?: boolean
  align?: 'left' | 'right' | 'center'
  sortable?: boolean
}
const columns = [
  {
    name: 'name',
    field: 'description',
    required: true,
    label: 'Projeto',
    align: 'left',
    style: 'width: 240px',
    sortable: true,
  },
  {
    name: 'executors',
    field: 'status',
    label: 'Executores',
    align: 'left',
    sortable: true,
  },
  {
    name: 'approvers',
    field: 'status',
    label: 'Aprovadores',
    align: 'left',
    sortable: true,
  },
  {
    name: 'revisors',
    field: 'status',
    label: 'Revisores',
    align: 'left',
    sortable: true,
  },
  {
    name: 'status',
    field: 'statusDisplay',
    label: 'Status',
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
    @row-click="(evt, row) => router.push(`/projeto/${row.id}`)"
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

    <template #body-cell-executors="props">
      <QTd :props="props">
        <MultiUsersCell :items="props.row.executors" />
      </QTd>
    </template>

    <template #body-cell-approvers="props">
      <QTd :props="props">
        <MultiUsersCell :items="props.row.approvers" />
      </QTd>
    </template>

    <template #body-cell-revisors="props">
      <QTd :props="props">
        <MultiUsersCell :items="props.row.revisors" />
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
</template>
