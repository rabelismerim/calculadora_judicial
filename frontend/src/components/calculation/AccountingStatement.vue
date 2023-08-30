<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: string
  creditor?: any
  recovering?: any
  calculationNumber?: string
}>(), {
})
const emit = defineEmits(['update:modelValue'])
let loading = $ref(false)
let isDownloading = $ref(false)

let content = $ref([] as any[])
const tabs = computed(() => content.map(({ label }: any, value: number) => ({ label, value })))
let contentSelected = $ref(-1)

const html = computed(() => {
  const index = contentSelected
  return `<!DOCTYPE html>
    <html lang="en">
      <head>
        <meta charset="utf-8">
        <title>title</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@400;700&display=swap');
          * { 
            font-family: 'Open Sans', Helvetica, Arial, sans-serif !important;
            font-size: 16px !important;
          }
          :root {
            --base: 0, 0%, 100%;
            --dark-base: 0, 0%, 0%;
            --secondary: 81, 68%, 44%;
          }
          body {
            margin: 0;
          }
          td {
            padding: 8px;
          }
          body,
          div {
            --bar: 5px;
            --bar-start: 0;
            --bar-end: 0;
            --bar-bg: var(--base);
          }
          ::-webkit-scrollbar {
            width: var(--bar);
            height: var(--bar);
            right: -100px;
          }
          ::-webkit-scrollbar-track {
            background: hsl(var(--bar-bg));
            margin-top: var(--bar-start);
            margin-left: var(--bar-start);
            margin-bottom: var(--bar-end);
            margin-right: var(--bar-end);
          }
          ::-webkit-scrollbar-thumb {
            box-shadow: inset 0 0 var(--bar) var(--bar) hsl(var(--dark-base),.3);
            transition: all 1s ease-in-out;
          }
          .dark ::-webkit-scrollbar-thumb {
            box-shadow: inset 0 0 var(--bar) var(--bar) #fff9;
          }
          ::-webkit-scrollbar-thumb:hover {
            box-shadow: inset 0 0 var(--bar) var(--bar) hsl(var(--secondary));
          }
          ::-webkit-scrollbar-button {
            display: none;
          }
        <\/style>
      </head>
      ${index > -1 ? (content[index]?.body || '') : ''}
    <\/html>`
})

const loadStatement = async () => {
  const calculationId = props.modelValue
  if (!calculationId)
    return
  loading = true
  try {
    const result = await calculationService.getAccountingStatement(calculationId)
    if (result.errors) {
      throwError({ id: 'ACCOUNTING_STATEMENT', message: result.errors })
      contentSelected = 0
      return
    }
    content = result
    contentSelected = 0
  }
  catch (error) {
    printError('ERROR ON LOAD ACCOUNTING STATEMENT', error)
  }
  finally {
    loading = false
  }
}

const downloadXLSX = async () => {
  const calculationId = props.modelValue
  if (!calculationId)
    return
  isDownloading = true
  try {
    const result = await calculationService.getAccountingStatementXLSX(calculationId)
    if (result.errors) {
      throwError({ id: 'ACCOUNTING_STATEMENT', message: result.errors })
      return
    }
    const date = new Date()
    const [day, month, year] = date
      .toLocaleDateString('en')
      .padStart(10, '0')
      .split('/')
    const fileName = `Calc_${props?.calculationNumber?.replaceAll(' ', '')}_${toKebab(props.recovering?.entity?.name)}_${toKebab(props.creditor?.entity?.name)}_${year}-${month}-${day}`

    saveFile(result, fileName, 'xlsx')
  }
  catch (error) {
    printError('ERROR ON LOAD ACCOUNTING STATEMENT', error)
  }
  finally {
    isDownloading = false
  }
}

onMounted(() => {
  loadStatement()
})
</script>

<template>
  <TabFilter v-model="contentSelected" :items="tabs">
    <template #side>
      <Btn
        label="Baixar Extrato Contábil"
        :loading="isDownloading"
        :disabled="isDownloading"
        loading-label="Baixando Extrato Contábil..."
        @click="downloadXLSX"
      />
    </template>
  </TabFilter>
  <div class="relative">
    <QLinearProgress
      v-if="loading"
      indeterminate
      color="secondary"
      class="absolute top-0 left-0"
      size="xs"
    />
    <iframe
      v-if="contentSelected > -1"
      ref="iframe"
      type="text/html"
      :srcdoc="html"
      class="w-full bg-white min-h-200 border-1 border-black/12"
    />
    <div v-else class="p-6 text-center text-lg">
      Carregando Extrato Contábil...
    </div>
  </div>
</template>
