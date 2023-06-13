<script setup lang='ts'>
const attrs = useAttrs() as any
const { dialog } = useQuasar()

let loading = $ref(false)

const menu = $ref('project')
const tab = $ref('cred')
const tabFilters = [
  { label: '1. Crédito', value: 'cred' },
  { label: '2. Extrato Contábil', value: 'ext' },
]

const headers: any = {
  'Content-type': 'application/json',
  'Accept': 'application/json',
  // TODO: BRING TO USER PREFERENCES
  'Accept-Language': 'pt-BR,pt;q=1',
}
if (import.meta.env.VITE_TOKEN)
  headers.Authorization = `Token ${import.meta.env.VITE_TOKEN}`
const host = import.meta.env.VITE_API_URL.slice(0, -9)

let project = $ref({} as any)
const loadProject = async () => {
  if (attrs.projectId)
    project = await projectService.getProject(attrs.projectId)
}

let creditor = $ref({} as any)
const loadCreditor = async () => {
  creditor = await creditorsService.getCreditor(attrs.creditorId)
}
const recovering = computed(() => project?.recoverings?.find(({ id }: any) => id === creditor?.recoveringId))

let options = $ref({} as any)
const loadOptions = async (calculationId: string) => {
  const users = await usersService.getUsers()
  const result = await creditorsService.getOptions()
  const { stepCalculationOptions = [] } = result
  const steps = []
  for (const step of stepCalculationOptions) {
    const error = await fetch(`${host}/juca/api/v1/calculation/${calculationId}/check_step/`, {
      method: 'PUT',
      headers,
      body: JSON.stringify({
        next_step: step?.id,
      }),
    })
      .then((result: any) => result?.json())
    if (!error?.data?.errors)
      steps.push(step)
  }
  result.steps = steps
  result.users = users
  options = result
}

let rates = $ref([] as any[])
const loadRates = async () => {
  rates = await ratesService.getRates()
}

let calculation = $ref({} as any)
const loadCalculation = async (showLoading = false) => {
  if (showLoading)
    loading = true
  const result = await calculationService.getCalculation(attrs.calculationId)
  const { allFunds = [] } = result
  result.credits = allFunds
    .flatMap(({ data, type }: any) => data.map((el: any) => ({ ...el, type })))
    .sort(({ createdAt: dateA }: any, { createdAt: dateB }: any) => dateA < dateB ? -1 : 1)
    .map((credit: any) => {
      credit.tables = credit?.template?.tables.map(({ fields, description, endPoint, id, many }: any) => {
        const columns = fields
          ?.map(({ id, isEditable, key, decimals, label, order, required, typeDisplay }: any) =>
            ({
              id,
              isEditable,
              decimals,
              name: key,
              field: key,
              label,
              order,
              required,
              type: typeDisplay,
              align: (isEditable && typeDisplay !== 'boolean') ? 'left' : 'center',
            }))
          .sort(({ order: orderA }: any, { order: orderB }: any) => orderA < orderB ? -1 : 1)
        columns.push({
          name: 'delete',
          field: 'delete',
          label: 'Apagar',
        })
        return { columns, description, endPoint, id, many, linesToAdd: 1, values: [] }
      })
      credit.summary = credit?.template?.summary
      return credit
    })
  calculation = result
  if (showLoading)
    loading = false
}

const showNewCredit = $ref(false)
const openCredit = async (credit: any) => {
  const { tables } = credit
  const isClear = tables
    .map(({ values }: any) => values?.length)
    .every((length: number) => length === 0)
  if (!isClear)
    return
  loading = true
  for (const table of tables as any[]) {
    const result = await fetch(`${host}${table.endPoint + credit.id}/`, { method: 'GET', headers })
      .then((result: any) => result.json())
      .then((result: any) => Object.values(Object.values(result).at(0) as any)
        .find((value: any) => Array.isArray(value)))
    table.values = result || clone([])
    if (table.values?.length === 0)
      table.values.push(clone({}))
  }
  loading = false
}
const addCreditValues = (data: any[], amount = 1) => {
  data.push(...Array(amount).fill(0).map(() => clone({})))
}
const removeCredit = (credit: any) => {
  dialog({
    title: 'Excluir Créditos',
    message: 'Você tem certeza que deseja excluir este Crédito?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading = true
    try {
      await calculationService.deleteCredit(credit)
      await loadCalculation()
      notify({ message: 'O Crédito foi apagado com sucesso!' })
    }
    catch (error) {
      printError('ERROR ON DELETE CREDIT:', error)
    }
    finally {
      loading = false
    }
  })
}
const removeCreditValue = async (values: any[], line: any, index: number, table: any) => {
  if (!line.id) {
    values.splice(index, 1)
    return
  }
  dialog({
    title: 'Excluir Linha',
    message: 'Você tem certeza que deseja excluir esta linha de Crédito?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    line.loading = true
    const result = await fetch(`${host}${`${table.endPoint}detail/${line.id}`}/`, { method: 'DELETE', headers })
      .then((result: any) => result.json())
      .then((result: any) => Object.values(Object.values(result).at(0) as any)?.at(1))
    line.loading = false
    if (Array.isArray(result) && result?.at(0)?.code)
      return
    values.splice(index, 1)
    notify({ message: 'Linha de Crédito excluida com sucesso!' })
  })
}
const forms = ref(null as any)
const calculateCredit = async (credit: any, creditIndex: number) => {
  const form = forms.value[creditIndex]
  const canSubmit = await form.validate()
  if (!canSubmit)
    return
  const { tables } = credit
  dialog({
    title: 'Processar Créditos',
    message: 'Você tem certeza que deseja processar estes créditos?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    loading = true
    for (const table of tables) {
      for (const lineIndex in table.values) {
        const line = table.values[lineIndex]
        table.values[lineIndex].loading = true
        const method = line.id ? 'PUT' : 'POST'
        const result: any = await fetch(`${host}${table.endPoint}${method === 'PUT' ? 'detail/' : ''}${line.id ? `${line.id}/` : ''}`, {
          method,
          body: JSON.stringify({ ...line, fund_id: credit.id, calculation_id: calculation.id }),
          headers,
        })
          .then(response => response.json())
          .then(response => Object.values(response).at(0))
        if (!result.errors)
          table.values[lineIndex] = result
        else
          table.values[lineIndex].loading = false
      }
    }
    notify({ message: 'Crédito processado com sucesso!' })
    loading = false
  })
}

const isRequired = ({ required }: any) => required && [(value: any) => !!value || 'Campo obrigatório!']

const creditsAmount = computed(() => calculation?.credits?.length || 0)
const classesAmount = computed(() => calculation?.classes?.length)
const totalValue = computed(() => calculation?.credits
  ?.map(({ total }: any) => total?.totalCorrected || 0)
  ?.reduce((acc: number, curr: number) => acc + curr || 0, 0))
onMounted(async () => {
  loading = true
  try {
    await loadProject()
    await loadCreditor()
    await loadCalculation()
    await loadOptions(calculation?.id)
    await loadRates()
  }
  catch (error) {
    printError('ERROR ON LOADING CALCULATION:', error)
  }
  finally {
    loading = false
  }
})

const stepColors: any = {
  S: '#AAAAAA', // To Calculate
  C: '#C4D600', // To Review
  E: '#86BC25', // To Approve
  B: '#43B02A', // To Approve Special
  A: '#007CB0', // Approved
  R: '#DA291C', // Failed
}
const statusColors: any = {
  S: '#c4d600', // Requested
  C: '#86BC25', // Concluded
  E: '#007cb0', // In Progress
  F: '#DA291C', // Calculation failed - rate not found
  G: '#DA291C', // Calculation failed - rate RJ not found
  H: '#DA291C', // Calculation failed - rate data base not found
  A: '#DA291C', // Calculation failed - aliquot not found
  P: '#DA291C', // Calculation failed - invalid parameters
  R: '#DA291C', // Calculation failed - no date RJ
  D: '#DA291C', // Calculation failed - no date Citation
  B: '#DA291C', // Calculation failed - in exclusion
}
const statusLabel = (status: string) => {
  if (status === 'S')
    return 'Solicitado'
  if (status === 'E')
    return 'Em Progresso'
  if (status === 'C')
    return 'Sucesso'
  if (['F', 'G', 'H', 'A', 'P', 'R', 'D', 'B'].includes(status))
    return 'Erro'
}

const history = computed(() => {
  const { historical = [], step = [] } = calculation?.historical || {}
  return [...historical.map((data: any) => ({ type: 'historical', ...data })), ...step.map((data: any) => ({ type: 'step', ...data }))]
    .sort(({ createdAt: a }: any, { createdAt: b }: any) => a < b ? -1 : 1)
})
const showChangeStatus = $ref(false)

const onPaste = (evt: any, table: any[], key: string, type: string, index: any) => {
  const clipBoardData = evt?.clipboardData?.getData('text') || ''
  const splitData = clipBoardData
    .split('\r\n')
    .map((item: string) => item.trim())
    .filter((item: string) => !!item)
  const values = (type === 'float' || type === 'integer')
    ? splitData
      .map((item: string) => Number(item.replaceAll('.', '').replaceAll(',', '.')))
    : splitData
  const data = table.slice(index, index + values.length)
  for (const index in data)
    data[index][key] = values[index]
}
</script>

<template>
  <Page
    menu-label="Dados do Projeto"
    :loading="loading"
    :links="[
      { label: 'Projetos', url: '/projetos' },
      { label: project.description, url: `/projeto/${attrs.projectId}` },
      { label: `Cálculo #${calculation?.number || ''}` }]"
  >
    <template #menuheader>
      <BtnToggle
        v-model="menu"
        class="bg--base w-[fit-content]"
        :items="[
          { label: 'Projeto', value: 'project' },
          { label: 'Sobre Cálculo', value: 'analysis' },
        ]"
      />
    </template>
    <template #menu>
      <CalculationMenu
        v-model="menu"
        :calculation="calculation"
        :creditor="creditor"
        :project="project"
        :recovering="recovering"
      />
    </template>

    <CalculationHeader
      :calculation="calculation"
      :colors="stepColors"
      @reload-click="loadCalculation(true)"
    >
      <Btn label="Alterar Status" outlined :disabled="!calculation?.id" @click="showChangeStatus = true" />
      <Btn label="Novo Crédito" icon="i-carbon-add-filled" :disabled="!calculation?.id" @click="showNewCredit = true" />
    </CalculationHeader>

    <TabFilter
      v-model="tab"
      :items="tabFilters"
    />

    <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 mb-8">
      <GraphCard
        title="Quantidade de Créditos"
        hint="O Número total dos Créditos neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          {{ creditsAmount }}
        </div>
      </GraphCard>
      <GraphCard
        title="Quantidade de Classes"
        hint="O Número total dos Classes neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          {{ classesAmount }}
        </div>
      </GraphCard>
      <GraphCard
        title="Total Geral de Créditos"
        hint="Somatório dos Créditos neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          R$ {{ totalValue?.toFixed(2) }}
        </div>
      </GraphCard>
    </div>

    <QTabPanels v-model="tab" animated class="calculations-credits">
      <QTabPanel name="cred">
        <div v-if="calculation?.credits?.length > 0" class="flex gap-4">
          <Accordion
            v-for="(credit, creditIndex) in calculation?.credits as any[]"
            :key="creditIndex"
            v-model="credit.isOpen"
            :title="`Crédito ${credit?.template?.name}`"
            :subtitle="credit.name"
            class="rounded-0"
            @open="openCredit(credit)"
          >
            <template #header-right>
              <div class="flex gap-2 self-center">
                <Btn
                  label="Excluir Crédito"
                  icon="i-carbon-trash-can"
                  transparent
                  @click.stop="removeCredit(credit)"
                />
              </div>
              <div class="self-center flex-1 flex justify-end text-lg flex gap-3">
                <div class="color-gray-9">
                  {{ credit.classes.classeDisplay }}
                </div>
                <div class="font-bold">
                  Total R$
                  {{ credit?.total?.totalCorrected?.toFixed(2) || 0 }}
                </div>
              </div>
            </template>
            <QForm ref="forms" @submit.prevent>
              <div
                v-for="table in credit?.tables as any[]"
                :key="table.id"
                class="p-4"
              >
                <div class="text-lg font-bold mb-2 flex justify-between items-center">
                  <div>{{ table.description }}</div>
                  <AddLines
                    v-model="table.linesToAdd"
                    @add-lines="addCreditValues(table.values, table.linesToAdd)"
                  />
                </div>
                <QTable
                  :rows="table.values"
                  :columns="table?.columns"
                  :pagination="{ rowsPerPage: 0 }"
                  hide-pagination
                  flat
                  bordered
                  class="credit-table"
                >
                  <template #body="props">
                    <QTr :props="props">
                      <QTd v-for="column in props.cols as any[]" :key="column.id" :style="(column?.isEditable) ? 'min-width: 200px' : '' ">
                        <div
                          class="flex justify-center items-center"
                          :class="{
                            'is-loading': props.row.loading,
                            'has-error': statusLabel(props.row?.status) === 'Erro',
                          }"
                        >
                          <div
                            v-if="column.name === 'delete'"
                            class="cursor-pointer bg--error h-10 w-10 rounded-.5 border-1 border-red-8 flex justify-center items-center"
                            @click="removeCreditValue(table.values, props.row, props.rowIndex, table)"
                          >
                            <div class="i-carbon-trash-can bg-white" />
                          </div>
                          <div v-else-if="column.label === 'Status'">
                            <StatusTag
                              v-if="props.row.status"
                              :label="statusLabel(props.row.status)"
                              :color="statusColors[props.row.status]"
                              :hint="props.row[column.field]"
                            />
                          </div>
                          <div v-else-if="!column.isEditable" class="row justify-center">
                            <span v-if="column.type === 'float'">{{ (get(column.field, props.row))?.toFixed(6) || '-' }}</span>
                            <span v-else>{{ get(column.field, props.row) || '-' }}</span>
                          </div>
                          <QInput
                            v-else-if="column.type === 'text'"
                            v-model="props.row[column.field]"
                            :rules="isRequired(column)"
                            class="flex-1"
                            outlined
                            dense
                            @paste.prevent="onPaste($event, table.values, column.field, column.type, props.rowIndex)"
                          />
                          <QInput
                            v-else-if="column.type === 'float' || column.type === 'integer'"
                            v-model="props.row[column.field]"
                            :rules="isRequired(column)"
                            class="flex-1"
                            type="number"
                            outlined
                            dense
                            @update:model-value="(value: any) => { if (column.type === 'integer') (props.row[column.field] = Math.round(value)) }"
                            @paste.prevent="onPaste($event, table.values, column.field, column.type, props.rowIndex)"
                          />
                          <InputDate
                            v-else-if="column.type === 'date'"
                            v-model="props.row[column.field]"
                            :rules="isRequired(column)"
                            class="flex-1"
                            @paste.prevent="onPaste($event, table.values, column.field, column.type, props.rowIndex)"
                          />
                          <div v-else-if="column.type === 'boolean'" class="row justify-center">
                            <QToggle
                              v-model="props.row[column.field]"
                              class="flex-1"
                            />
                          </div>
                        </div>
                      </QTd>
                    </QTr>
                  </template>
                </QTable>
              </div>
              <div class="flex gap-2 justify-between p-4 bg--primary/12 border--primary border-t-2 color--primary font-bold">
                <div>
                  <div>
                    Quantidade de Créditos:
                    {{ credit.tables.reduce((acc:number, table: any) => acc + table.values?.length, 0) }}
                  </div>
                  <div>
                    Total dos Valores: R$
                    {{ credit.tables.reduce((acc:number, table: any) => acc + (table.total || 0), 0)?.toFixed(2) }}
                  </div>
                </div>
                <div>
                  <div>
                    Calculados com Sucesso:
                    {{ credit.tables.reduce((acc:number, table: any) => acc + table.values?.filter((line: any) => statusLabel(line.status) === 'Sucesso')?.length, 0) }}
                  </div>
                  <div>
                    Calculados com Erro:
                    {{ credit.tables.reduce((acc:number, table: any) => acc + table.values?.filter((line: any) => statusLabel(line.status) === 'Erro')?.length, 0) }}
                  </div>
                </div>
                <Btn label="Processar" @click="calculateCredit(credit, creditIndex)" />
              </div>
            </QForm>
          </Accordion>
        </div>
        <div v-else class="text-lg text-center">
          Nenhum Crédito listado para este Cálculo...
        </div>
      </QTabPanel>
      <QTabPanel name="ext">
        <AccountingStatement v-model="calculation.id" />
      </QTabPanel>
    </QTabPanels>

    <template #out>
      <ChangeStatus
        v-model="showChangeStatus"
        :history="history"
        :options="options"
        :calculation-id="calculation?.id"
        @update-status="loadOptions(calculation?.id); loadCalculation()"
      />
      <NewCredit
        v-model="showNewCredit"
        :options="options"
        :calculation-id="attrs.calculationId"
        :rates="rates"
        :host="host"
        @success="loadCalculation"
      />
    </template>
  </Page>
</template>

<style>
[projectId], [calculationId] {
  display: flex;
  flex: 1;
}
.calculation-details .q-panel.scroll,
.credit-table .q-table__middle.scroll {
  overflow-y: hidden;
}
.credit-table .q-field--with-bottom {
  padding: 0;
}
.credit-table .q-field--error .q-field__bottom {
  padding: 0;
}
.credit-table .q-field--error .q-field__bottom div[role=alert] {
  background-color: var(--q-negative);
  color: #fff;
  padding: 4px;
  display: flex;
  justify-content: center;
  border-radius: 0 0 4px 4px;
  margin-top: -2px;
}
.calculations-credits {
  background: transparent;
}
.calculations-credits .q-tab-panel {
padding: 0;
}
</style>
