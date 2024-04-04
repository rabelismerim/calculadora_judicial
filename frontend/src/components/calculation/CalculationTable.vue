<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue?: any[]
  validation?: boolean
  creditor?: any
}>(), {
  modelValue: () => [],
  validation: false,
})

const emit = defineEmits(['update:modelValue', 'rowClick', 'update:validation', 'validated'])
const { dialog } = useQuasar()

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
  if (!props.validation || step !== 'A')
    return
  const rowIndex = selectedRows?.findIndex((value: number) => index === value)
  if (rowIndex > -1) {
    selectedRows.splice(rowIndex, 1)
    return
  }
  selectedRows.push(index)
}
const onValidation = () => {
  dialog({
    title: 'Validando Cálculos',
    message: 'Você tem certeza que deseja validar estes cálculos?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading = true
    try {
      const items = selectedRows.map((index: number) => props.modelValue[index].id)
      await creditorsService.validateCalculations(props.creditor.id || '', items)
      notify({ message: 'Cálculos validados com sucesso!' })
    }
    catch (error) {
      printError('ERROR ON VALIDATING CALCULATION TABLE:', error)
    }
    finally {
      loading = false
      emit('update:validation', false)
      emit('validated')
    }
  })
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
    format: (value: any) => value?.number ?? '-',
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
    format: (value: any) => {
      if (value?.classeDisplay)
        return value?.classeDisplay ?? '-'
      if (!value || !Array.isArray(value))
        return '-'

      const filteredValue = value.filter(({ percentageCalculated }: any) => {
        return percentageCalculated !== 0
      })

      const formattedValue = filteredValue.map(({ classeDisplay, percentageCalculated }: any) => {
        const formattedString = `${classeDisplay?.split('-').at(0).trim()}: ${formatNumber(percentageCalculated || 0, 2)}%`
        return formattedString
      }).join(' ,')
      return formattedValue || '-'
    },
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
    field: 'specialApprovers',
    label: 'Aprovadores Especiais',
    align: 'left',
    sortable: true,
  },
  {
    name: 'coin',
    field: 'coins',
    label: 'Moeda',
    align: 'left',
    sortable: true,
    format: (value: any) => value?.coinDisplay ?? '-',
  },
  {
    name: 'referenceValue',
    field: 'coins',
    label: 'Referência',
    align: 'left',
    sortable: true,
    format: (value: any) => typeOf(value?.value) === 'Number' ? formatNumber(value?.value, 2) : '-',
  },
  {
    name: 'total',
    field: 'allFunds',
    format: (value: any = []) => {
      if (typeOf(value) === 'Number')
        return formatNumber(value, 2)
      return formatNumber(value
        ?.flatMap(({ data }: any) => data)
        ?.map((credit: any) => (typeof credit?.total === 'number' ? credit?.total : credit?.total?.totalCorrected) || 0)
        ?.reduce((acc: number, cur: number) => acc + cur, 0), 2) || '-'
    },
    label: 'Calculado',
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

const handleRowClick = (evt: Event, row: any) => {
  const target = (evt.target) as HTMLElement
  if (['AJ', 'RJ'].includes(row.number)) {
    target.style.cursor = 'auto'
    return
  }
  emit('rowClick', row)
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
    @row-click="(evt: Event, row: any) => handleRowClick(evt, row)"
  >
    <template #header-cell-action="prop">
      <QTh :props="prop" class="w-2">
        <button
          class="rounded hover:bg--base active:bg--secondary p-2 tween"
          @click="toggleFullScreen"
        >
          <div :class="inFullScreen ? 'i-carbon-minimize' : 'i-carbon-maximize'" />
        </button>
      </QTh>
    </template>
    <template #body-cell-action="prop">
      <QTd class="flex justify-center items-center">
        <div
          v-if="!['AJ', 'RJ'].includes(prop.row?.number)"
          class="w-2 h-2 block rounded-full"
          :class="prop.row.validated ? 'bg--secondary' : 'bg--error'"
        />
      </QTd>
    </template>
    <template #body-cell-executor="prop">
      <QTd>
        <div
          v-if="['AJ', 'RJ'].includes(prop.row?.number)"
          class="w-2 h-2 block rounded-full"
        >
          -
        </div>
        <div v-else-if="prop.value">
          {{ prop.value }}
        </div>
        <div
          v-else
          class="i-carbon-warning-filled color--error text-lg"
        />
      </QTd>
    </template>
    <template #body-cell-reviewer="prop">
      <QTd>
        <div
          v-if="['AJ', 'RJ'].includes(prop.row?.number)"
          class="w-2 h-2 block rounded-full"
        >
          -
        </div>
        <div v-else-if="prop.value">
          {{ prop.value }}
        </div>
        <div
          v-else
          class="i-carbon-warning-filled text-lg color-gray"
          :class="{ 'color--error': prop.row.executor }"
        />
      </QTd>
    </template>
    <template #body-cell-approver="prop">
      <QTd>
        <div
          v-if="['AJ', 'RJ'].includes(prop.row?.number)"
          class="w-2 h-2 block rounded-full"
        >
          -
        </div>
        <div v-else-if="prop.value">
          {{ prop.value }}
        </div>
        <div
          v-else
          class="i-carbon-warning-filled text-lg color-gray"
          :class="{ 'color--error': prop.row.reviewer }"
        />
      </QTd>
    </template>
    <template #body-cell-specialapprover="prop">
      <QTd>
        <div
          v-if="['AJ', 'RJ'].includes(prop.row?.number)"
          class="w-2 h-2 block rounded-full"
        >
          -
        </div>
        <div v-else-if="prop.value?.length" class="flex gap-2">
          <div v-for="approver in prop.value as any[]" :key="approver.id">
            <UserPicture
              v-model="approver.projectUser"
              class="h-8 w-8 rounded-full border-3"
              :class="{
                'border--secondary': approver?.approved,
                'border-yellow': !approver?.approved,
              }"
            />
          </div>
          <QTooltip class="pt-3">
            <div
              v-for="approver in prop.value as any[]"
              :key="approver.id"
              class="flex gap-2 items-center mb-2"
            >
              <UserPicture
                v-model="approver.projectUser"
                class="h-7 w-7"
              />
              <div>{{ approver?.projectUser?.fullName }}</div>
              <StatusTag
                :label="approver?.approved ? 'Aprovou' : 'Aguardando aprovação...'"
                :color="approver?.approved ? '#87bc24' : '#c4d600'"
              />
            </div>
          </QTooltip>
        </div>
        <div
          v-else-if="prop.row.step === 'B'"
          class="i-carbon-warning-filled text-lg color-gray"
          :class="{ 'color--error': prop.row.reviewer }"
        />
        <div v-else>
          N/A
        </div>
      </QTd>
    </template>
    <template #body-cell-status="prop">
      <QTd :props="prop">
        <div class="flex">
          <StatusTag
            :label="prop.value"
            :color="statusColors[prop.row.step]"
          />
        </div>
      </QTd>
    </template>
    <template #body-cell-validated="prop">
      <QTd
        :props="prop"
        :class="{
          'is-validated': prop.row.validated,
          'cursor-not-allowed color-gray-6': !validation || loading || prop.row.step !== 'A',
          'color--primary': validation,
        }"
      >
        <div
          v-if="!['AJ', 'RJ'].includes(prop.row?.number)"
          class="w-2 h-2 block rounded-full"
          @click.stop="selectRow(prop.rowIndex, prop.row?.step)"
        >
          <div
            class="text-lg"
            :class="selectedRows.includes(prop.rowIndex) ? 'i-carbon-checkbox-checked-filled' : 'i-carbon-checkbox'"
          />
        </div>
      </QTd>
    </template>
  </QTable>
  <div class="flex justify-between items-center py-2 pl-8 pr-5 border-t-3 color--primary font-bold text-lg border--primary bg--primary/12">
    <div>
      Quantidade de Cálculos Validados:
      {{ modelValue?.reduce((acc: number, curr: any) => curr?.validated ? acc + 1 : acc, 0) }}
    </div>
    <div class="flex gap-6 items-center">
      <div>
        Valor Total Validado:
        R$ {{ formatNumber(creditor.total, 2) }}
      </div>
      <Btn
        v-if="validation === false"
        label="Validar Cálculos"
        :disabled="modelValue?.filter(({ step }) => step === 'A').length === 0"
        @click="emit('update:validation', true)"
      />
      <div v-else class="flex gap-3">
        <Btn
          label="Cancelar"
          :disabled="loading"
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
.calculation-table .is-validated {
  background-color: hsla(var(--secondary, 0, 0%, 0%), 0.05);
}
</style>
