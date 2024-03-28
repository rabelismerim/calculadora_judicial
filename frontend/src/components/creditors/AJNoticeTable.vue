<script setup lang="ts">
import { defineProps } from 'vue'

const props = defineProps({
  notices: {
    type: Array,
    required: true,
  },
})

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

const AJNoticeColumns: TableColumn[] = [
  {
    name: 'classeDisplay',
    field: 'classes',
    label: 'Classe',
    align: 'left',
    sortable: true,
  },
  {
    name: 'coin',
    field: 'coins',
    label: 'Moeda',
    align: 'left',
    sortable: true,
  },
  {
    name: 'value',
    field: 'coins',
    label: 'Valor',
    align: 'left',
    sortable: true,
  },
]
</script>

<template>
  <QTable
    ref="ajNoticeTable"
    :rows="notices"
    :columns="AJNoticeColumns"
    flat
    class="aj-notice-table"
    :pagination="{ rowsPerPage: 0 }"
    hide-pagination
  >
    <template #body-cell-classe="prop">
      <QTd
        class="flex justify-center items-center"
        :props="prop"
      >
        {{ prop.row.classes?.classeDisplay || '-' }}
        <div
          class="w-2 h-2 block rounded-full"
          :class="prop.row.validated ? 'bg--secondary' : 'bg--error'"
        />
      </QTd>
    </template>

    <template #body-cell-coin="prop">
      <QTd :props="prop">
        {{ prop.row.coins?.coin || '-' }}
      </QTd>
    </template>

    <template #body-cell-value="prop">
      <QTd :props="prop">
        {{ prop.row.coins?.value || '-' }}
      </QTd>
    </template>
  </QTable>
</template>
