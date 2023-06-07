<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue?: any[]
  validation?: boolean
  creditorId?: string
}>(), {
  modelValue: () => [],
  validation: false,
})
const emit = defineEmits(['update:modelValue', 'rowClick', 'update:validation', 'validated'])

let loading = $ref(false)

let inFullScreen = $ref(false)
const calculationsTable: any = ref(null as any)
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

let selectedRows: number[] = $ref([])
const resetValidation = () => {
  selectedRows = []
  props.modelValue
    .forEach(({ step, validated }: any, index: number) => {
      if (step === 'A' && validated)
        selectedRows.push(index)
    })
  emit('update:validation', false)
}
watchEffect(() => {
  resetValidation()
})
const selectRow = (index: number, step: string) => {
  if (step !== 'A')
    return
  const rowIndex = selectedRows.findIndex((value: number) => index === value)
  if (rowIndex > -1) {
    selectedRows.splice(rowIndex, 1)
    return
  }
  selectedRows.push(index)
}
const onValidation = async () => {
  loading = true
  try {
    const items = selectedRows.map((index: number) => props.modelValue[index].id)
    await creditorsService.validateCalculations(props.creditorId || '', items)
    notify({ message: 'Cálculos validados com sucesso!' })
  }
  catch (error) {
    printError('ERROR ON VALIDATING CREDITORS TABLE:', error)
  }
  finally {
    loading = false
    emit('update:validation', false)
    emit('validated')
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
    field: 'isAdm',
    format: (isAdm: boolean) => isAdm ? 'Administrativa' : 'Judicial',
    label: 'Fase',
    align: 'left',
    sortable: true,
  },
  {
    name: 'class',
    field: 'classes',
    format: (value: any[]) => value && value
      .filter(({ percentageCalculated }: any) => !!percentageCalculated)
      .map(({ classeDisplay, percentageCalculated }: any) => `${classeDisplay?.split('-').at(0).trim()}: ${(percentageCalculated || 0)?.toFixed(2)}%`).join(' ,'),
    label: 'Classe',
    align: 'left',
    sortable: true,
  },
  {
    name: 'executor',
    field: 'executor',
    label: 'Executor',
    format: (value: any) => value?.fullName,
    align: 'left',
    sortable: true,
  },
  {
    name: 'reviewer',
    field: 'reviewer',
    label: 'Revisor',
    format: (value: any) => value?.fullName,
    align: 'left',
    sortable: true,
  },
  {
    name: 'approver',
    field: 'approver',
    label: 'Aprovador',
    format: (value: any) => value?.fullName,
    align: 'left',
    sortable: true,
  },
  {
    name: 'specialapprover',
    field: 'specialApprover',
    label: 'Aprovador Especial',
    format: (value: any) => value?.fullName,
    align: 'left',
    sortable: true,
  },
  {
    name: 'total',
    field: 'statement',
    format: (value: any) => value?.total ? (+value.total)?.toFixed(2) : '-',
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

const statusColors: any = {
  S: '#AAAAAA', // To Calculate
  C: '#C4D600', // To Review
  E: '#86BC25', // To Approve
  B: '#43B02A', // To Approve Special
  A: '#007CB0', // Approved
  R: '#DA291C', // Failed
}
</script>

<template>
  <QTable
    ref="calculationsTable"
    :rows="modelValue"
    :columns="calculationColumns"
    flat
    class="calculation-table"
    :pagination="{ rowsPerPage: 0 }"
    hide-pagination
    @row-click="(evt, row) => emit('rowClick', row)"
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
    <template #body-cell-action="props">
      <QTd class="flex justify-center items-center">
        <div
          class="w-2 h-2 block rounded-full"
          :class="props.row.validated ? 'bg--primary' : 'bg--error'"
        />
      </QTd>
    </template>
    <template #body-cell-executor="props">
      <QTd>
        <div v-if="props.value">
          {{ props.value }}
        </div>
        <div
          v-else
          class="i-carbon-warning-filled color--error text-lg"
        />
      </QTd>
    </template>
    <template #body-cell-reviewer="props">
      <QTd>
        <div v-if="props.value">
          {{ props.value }}
        </div>
        <div
          v-else
          class="i-carbon-warning-filled text-lg color-gray"
          :class="{ 'color--error': props.row.executor }"
        />
      </QTd>
    </template>
    <template #body-cell-approver="props">
      <QTd>
        <div v-if="props.value">
          {{ props.value }}
        </div>
        <div
          v-else
          class="i-carbon-warning-filled text-lg color-gray"
          :class="{ 'color--error': props.row.reviewer }"
        />
      </QTd>
    </template>
    <template #body-cell-specialapprover="props">
      <QTd>
        <div v-if="props.value">
          {{ props.value }}
        </div>
        <div
          v-else-if="props.row.step === 'B'"
          class="i-carbon-warning-filled text-lg color-gray"
          :class="{ 'color--error': props.row.reviewer }"
        />
        <div v-else>
          N/A
        </div>
      </QTd>
    </template>
    <template #body-cell-status="props">
      <QTd :props="props">
        <div class="flex">
          <StatusTag
            :label="props.value"
            :color="statusColors[props.row.step]"
          />
        </div>
      </QTd>
    </template>
    <template #body-cell-validated="props">
      <QTd
        :props="props"
        :class="{
          'is-validated': props.row.validated,
          'cursor-not-allowed color-gray-6': !validation || loading || props.row.step !== 'A',
          'color--primary': validation,
        }"
      >
        <div
          class="flex"
          @click.stop="selectRow(props.rowIndex, props.row?.step)"
        >
          <div
            class="text-lg"
            :class="selectedRows.includes(props.rowIndex) ? 'i-carbon-checkbox-checked-filled' : 'i-carbon-checkbox'"
          />
        </div>
      </QTd>
    </template>
  </QTable>
  <div class="flex justify-between items-center py-2 pl-8 pr-5 border-t-3 color--primary font-bold text-lg border--primary bg--primary/12">
    <div>
      Quantidade de Cálculos Validados:
      {{ modelValue?.reduce((acc: number, curr: any) => curr?.validated ? acc++ : acc, 0) }}
    </div>
    <div class="flex gap-6 items-center">
      <div>
        Valor Total Validado:
        {{ modelValue?.reduce((acc: number, curr: any) => curr?.statement?.total ? +curr?.statement?.total + acc : acc, 0)?.toFixed(2) }}
      </div>
      <Btn v-if="validation === false" label="Validar Cálculos" @click="emit('update:validation', true)" />
      <div v-else class="flex gap-3">
        <Btn
          label="Cancelar"
          :dosabled="loading"
          outlined
          @click="resetValidation"
        />
        <Btn
          label="Salvar"
          :loading="loading"
          :disabled="loading"
          loading-label="Salvando Validações..."
          @click="onValidation"
        />
      </div>
    </div>
  </div>
</template>

<style>
.calculation-table tr:has(.is-validated) {
  background-color: hsla(var(--primary,0,0%,0%),0.10)
}
</style>
