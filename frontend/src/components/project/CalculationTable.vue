<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue?: any[]
}>(), {
  modelValue: () => [],
})
const emit = defineEmits(['update:modelValue', 'row-click'])

let inFullScreen = $ref(false)
const calculationsTable: any = ref(null)
const toggleFullScreen = () => {
  if (!inFullScreen) {
    calculationsTable.value.setFullscreen()
    inFullScreen = true
  }
  else {
    calculationsTable.value.exitFullscreen()
    inFullScreen = false
  }
}
interface TableColumn {
  name: string
  label: string
  field: string
  required?: boolean
  align?: 'left' | 'right' | 'center'
  sortable?: boolean
  style?: string
  format?: (val: any, row: any) => any
}
const calculationColumns: TableColumn[] = [
  {
    name: 'action',
    label: '-',
    field: '-',
    align: 'left',
  },
  {
    name: 'id',
    field: 'number',
    label: 'Id',
    required: true,
    align: 'left',
    style: 'width: 100px',
    sortable: true,
  },
  {
    name: 'incident',
    field: 'incident',
    format: ({ number }: any) => number || '-',
    label: 'N° Incidente',
    align: 'left',
    style: 'width: 100px',
    sortable: true,
  },
  {
    name: 'created',
    field: 'createdAt',
    format: (date: string) => formatDateFromBackend(date),
    label: 'Data de Criação',
    align: 'left',
    sortable: true,
  },
  {
    name: 'fase',
    field: 'fase',
    format: () => '-',
    label: 'Fase',
    align: 'left',
    sortable: true,
  },
  {
    name: 'class',
    field: 'class',
    format: () => '-',
    label: 'Classe',
    align: 'left',
    sortable: true,
  },
  {
    name: 'executor',
    field: 'excecutor',
    format: () => '-',
    label: 'Executor',
    align: 'left',
    sortable: true,
  },
  {
    name: 'revisor',
    field: 'revisor',
    format: () => '-',
    label: 'Revisor',
    align: 'left',
    sortable: true,
  },
  {
    name: 'approver',
    field: 'approver',
    format: () => '-',
    label: 'Aprovador',
    align: 'left',
    sortable: true,
  },
  {
    name: 'specialApprover',
    field: 'specialApprover',
    format: () => '-',
    label: 'Aprovador Especial',
    align: 'left',
    sortable: true,
  },
  {
    name: 'total',
    field: 'value',
    format: () => '-',
    label: 'Valor',
    align: 'left',
    sortable: true,
  },
  {
    name: 'status',
    field: 'stepDisplay',
    label: 'Status',
    align: 'left',
    sortable: true,
  },
  {
    name: 'validated',
    field: 'validated',
    label: 'Validado',
    align: 'left',
    sortable: true,
  },
]
</script>

<template>
  <QTable
    ref="calculationsTable"
    :rows="modelValue"
    :columns="calculationColumns"
    flat
    class="calculation-table"
    @row-click="(evt, row) => emit('row-click', row)"
  >
    <template #header-cell-action="props">
      <QTh :props="props" class="w-2">
        <button
          class="rounded hover:bg--base active:bg--secondary p-2 tween"
          @click="toggleFullScreen"
        >
          <div :class="inFullScreen ? 'i-carbon-minimize' : 'i-carbon-maximize'" />
        </button>
      </QTh>
    </template>
    <template #body-cell-action>
      <QTd class="flex justify-center items-center">
        <div
          class="bg-gray-4 w-2 h-2 block rounded-full"
        />
      </QTd>
    </template>
  </QTable>
</template>
