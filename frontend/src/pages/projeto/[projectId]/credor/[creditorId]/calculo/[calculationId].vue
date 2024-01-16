<script setup lang='ts'>
const attrs = useAttrs() as any
const { dialog } = useQuasar()

const { hasPermissions, login } = $user

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
  'Accept-Language': 'pt-BR,pt;q=1',
  'X-CSRFToken': getCookie('csrftoken'),
}
if (import.meta.env.VITE_TOKEN)
  headers.Authorization = `Token ${import.meta.env.VITE_TOKEN}`
const host = import.meta.env.VITE_API_HOST

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
const loadOptions = async () => {
  const users = await usersService.getUsers()
  const result = await creditorsService.getOptions()
  const { stepCalculationOptions = [] } = result
  const steps = []
  for (const step of stepCalculationOptions) {
    const error = await fetch(`${host}/juca/api/v1/calculation/${attrs.calculationId}/check_step/`, {
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
const loadCalculationBigNumbers = async () => {
  try {
    const result = await calculationService.getCalculation(attrs.calculationId)
    result.allFunds
      .flatMap(({ data, type }: any) => data.map((el: any) => ({ ...el, type })))
      .sort(({ createdAt: dateA }: any, { createdAt: dateB }: any) => dateA < dateB ? -1 : 1)
      .forEach(({ id, total }: any) => {
        const credit = calculation?.credits?.find(({ id: creditId }: any) => creditId === id)
        if (credit)
          credit.total = total
      })
  }
  catch (error) {
    printError('ERROR ON LOADING CREDITS BIG NUMBERS:', error)
  }
}
const loadCalculation = async (showLoading = false) => {
  if (showLoading)
    loading = true
  const result = await calculationService.getCalculation(attrs.calculationId)
  const { allFunds = [] } = result
  result.credits = allFunds
    .flatMap(({ data, type }: any) => data.map((el: any) => ({ ...el, type })))
    .sort(({ createdAt: dateA }: any, { createdAt: dateB }: any) => dateA < dateB ? -1 : 1)
    .map((credit: any) => {
      credit.tables = credit?.template?.tables.map(({ fields, description, endPoint, id, many, summary }: any) => {
        const columns = fields
          ?.map(({ id, isEditable, key, decimals, label, order, required, typeDisplay, default: defaultValue, choices }: any) =>
            ({
              id,
              isEditable,
              decimals,
              defaultValue,
              name: key,
              field: key,
              label,
              order,
              required,
              sortable: ['float', 'integer', 'date'].includes(typeDisplay),
              type: typeDisplay,
              align: (isEditable && typeDisplay !== 'boolean') ? 'left' : 'center',
              choices,
            }))
          .sort(({ order: orderA }: any, { order: orderB }: any) => orderA < orderB ? -1 : 1)
        if (many) {
          columns.push({
            name: 'delete',
            field: 'delete',
            label: 'Apagar',
          })
        }
        return { summary, columns, description, endPoint, id, many, linesToAdd: 1, values: [] }
      })
      credit.summary = credit?.template?.summary
      return credit
    })
  calculation = result
  if (showLoading)
    loading = false
}
let bigNumbers: any = $ref({})
const loadBigNumbers = async (withCredits = false) => {
  try {
    bigNumbers = await calculationService.getCalculationBigNumbers(attrs.calculationId)
    if (withCredits)
      loadCalculationBigNumbers()
  }
  catch (error) {
    printError('ERROR ON LOADING PROJECT BIG NUMBERS:', error)
  }
}

const showNewCredit = $ref(false)
const addCreditValues = (table: any, amount = 1) => {
  const defaultValue = Object.fromEntries(table.columns
    .filter(({ defaultValue }: any) => defaultValue !== null)
    .map(({ field, defaultValue }: any) => [field, defaultValue]))
  table.values?.push(...Array(amount).fill(0).map(() => clone(defaultValue)))
}
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
    const entries = Object.entries(Object.values(result).at(0) as any)
    const values = entries
      ?.find(([,value]) => Array.isArray(value))
    const data = entries
      ?.filter(([, value]) => !Array.isArray(value))
    table.values = values?.[1] || clone([])
    table.data = Object.fromEntries(data)
    if (table.values?.length === 0)
      addCreditValues(table, 1)
  }
  loading = false
}
const openCreditBigNumbers = async (credit: any) => {
  const { tables } = credit
  loading = true
  for (const table of tables as any[]) {
    const result = await fetch(`${host}${table.endPoint + credit.id}/`, { method: 'GET', headers })
      .then((result: any) => result.json())
    const entries = Object.entries(Object.values(result).at(0) as any)
    const data = entries
      ?.filter(([, value]) => !Array.isArray(value))
    table.data = Object.fromEntries(data)
  }
  loading = false
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
      loadBigNumbers()
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
    loadBigNumbers(true)
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
        const result: any = await fetch(`${host}${table.endPoint}${(method === 'PUT' && !table.endPoint.endsWith('/detail/')) ? 'detail/' : ''}${line.id ? `${line.id}/` : ''}`, {
          method,
          body: JSON.stringify({ ...line, fund_id: credit.id, calculation_id: attrs.calculationId }),
          headers,
        })
          .then(response => response.json())
          .then(response => Object.values(response).at(0))
        if (!result.errors) {
          table.values[lineIndex] = result
        }
        else {
          table.values[lineIndex].status = 'ERROR'
          table.values[lineIndex].status_display = result.errors?.[0]?.detail
        }

        table.values[lineIndex].loading = false
      }
    }
    notify({ message: 'Crédito processado com sucesso!' })
    loading = false
    await openCreditBigNumbers(credit)
    await loadBigNumbers(true)
  })
}

const isRequired = ({ required }: any) => required && [(value: any) => value !== undefined || 'Campo obrigatório!']

onMounted(async () => {
  loading = true
  try {
    await login()
    await loadBigNumbers()
    await loadCalculation()
    await loadProject()
    await loadCreditor()
    await loadOptions()
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
  I: '#c4d600', // In Progress
  F: '#DA291C', // Calculation failed - rate not found
  G: '#DA291C', // Calculation failed - rate RJ not found
  H: '#DA291C', // Calculation failed - rate data base not found
  A: '#DA291C', // Calculation failed - aliquot not found
  P: '#DA291C', // Calculation failed - invalid parameters
  R: '#DA291C', // Calculation failed - no date RJ
  D: '#DA291C', // Calculation failed - no date Citation
  B: '#DA291C', // Calculation failed - in exclusion
  ERROR: '#DA291C', // Local Error
}
const statusLabel = (status: string) => {
  if (status === 'S')
    return 'Solicitado'
  if (status === 'E')
    return 'Em Progresso'
  if (status === 'I')
    return 'Registrado'
  if (status === 'C')
    return 'Sucesso'
  if (['F', 'G', 'H', 'A', 'P', 'R', 'D', 'B', 'ERROR'].includes(status))
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
  const values = (() => {
    if (type === 'text')
      return splitData
    if (type === 'float' || type === 'integer') {
      return splitData
        .map((item: string) => getValidNumber(item))
    }
    if (type === 'date') {
      return splitData
        .map((item: string) => getValidDate(item))
    }
  })()
  const data = table.slice(index, index + values?.length)
  for (const index in data)
    data[index][key] = values[index]
}

const getSummary = (orderItem: number, summaryList: any[] = []) => summaryList
  .find(({ order }: any) => orderItem === order)
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
      <Btn
        label="Alterar Status"
        outlined
        :disabled="!calculation?.id"
        @click="showChangeStatus = true"
      />
      <Btn
        v-if="hasPermissions('add_calculation')"
        label="Novo Crédito"
        icon="i-carbon-add-filled"
        :disabled="!calculation?.id || ['A', 'B'].includes(calculation?.step)"
        @click="showNewCredit = true"
      />
    </CalculationHeader>

    <TabFilter
      v-model="tab"
      :items="tabFilters"
    />

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      <GraphCard
        title="Quantidade de Créditos"
        hint="O Número total dos Créditos neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          {{ bigNumbers?.countFunds || '-' }}
        </div>
      </GraphCard>
      <GraphCard
        title="Quantidade de Classes"
        hint="O Número total dos Classes neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          {{ bigNumbers?.countClasses || '-' }}
        </div>
      </GraphCard>
      <GraphCard
        title="Total Histórico de Créditos"
        hint="Somatório dos Créditos neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          R$ {{ formatNumber(bigNumbers?.totalHistorical || 0, 2) }}
        </div>
      </GraphCard>
      <GraphCard
        title="Total Calculado de Créditos"
        hint="Somatório dos Créditos neste Cálculo."
      >
        <div class="font-bold text-5xl flex-1 flex items-center">
          R$ {{ formatNumber(bigNumbers?.total || 0, 2) }}
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
            :title="`Crédito ${credit?.template?.name} - ${credit?.rate?.index}`"
            :subtitle="credit.name"
            class="rounded-0"
            @open="openCredit(credit)"
          >
            <template #header-right>
              <div class="self-center flex-1 flex justify-end text-lg flex gap-3">
                <div class="color-gray-9">
                  {{ credit.classes.classeDisplay }}
                </div>
                <div class="font-bold">
                  Total R$
                  {{ formatNumber((typeof credit?.total === 'number' ? credit?.total : credit?.total?.totalCorrected) || 0, 2) }}
                </div>
              </div>
              <div class="flex gap-2 self-center">
                <Btn
                  v-if="!['A', 'B'].includes(calculation?.step)"
                  label="Excluir Crédito"
                  icon="i-carbon-trash-can"
                  transparent
                  :disabled="['A', 'B'].includes(calculation?.step) || !hasPermissions('delete_calculation')"
                  @click.stop="removeCredit(credit)"
                />
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
                    v-if="!['A', 'B'].includes(calculation?.step) && table.many"
                    v-model="table.linesToAdd"
                    @add-lines="addCreditValues(table, table.linesToAdd)"
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
                      <QTd
                        v-for="column in props.cols as any[]"
                        :key="column.id"
                        :style="(column?.isEditable) && column.type !== 'boolean'
                          ? (column?.isEditable) && column.type === 'text'
                            ? 'min-width: 200px; width: 10%' : 'min-width: 150px; width: 10%'
                          : '' "
                      >
                        <div
                          class="flex justify-center items-center"
                          :class="{
                            'is-loading': props.row.loading,
                            'has-error': statusLabel(props.row?.status) === 'Erro',
                          }"
                        >
                          <button
                            v-if="column.name === 'delete' && table.many"
                            class="cursor-pointer bg--error h-10 w-10 rounded-.5 border-1 border-red-8 flex justify-center items-center"
                            :disabled="['A', 'B'].includes(calculation?.step) || (props.row?.id && !hasPermissions('delete_calculation'))"
                            @click.stop="removeCreditValue(table.values, props.row, props.rowIndex, table)"
                          >
                            <div class="i-carbon-trash-can bg-white" />
                          </button>
                          <div v-else-if="column.label === 'Status'" :class="{ 'has-error': props.row.status === 'ERROR' }">
                            <StatusTag
                              v-if="props.row.status"
                              :label="statusLabel(props.row.status)"
                              :color="statusColors[props.row.status]"
                              :hint="props.row[column.field]"
                            />
                          </div>
                          <div v-else-if="!column.isEditable" class="row justify-center">
                            <span v-if="column.type === 'float'">{{ formatNumber(get(column.field, props.row), column.decimals) || '-' }}</span>
                            <span v-else>{{ get(column.field, props.row) || '-' }}</span>
                          </div>
                          <QInput
                            v-else-if="column.type === 'text'"
                            v-model="props.row[column.field]"
                            :rules="isRequired(column)"
                            class="flex-1"
                            outlined
                            dense
                            :disable="['A', 'B'].includes(calculation?.step)"
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
                            :disable="['A', 'B'].includes(calculation?.step)"
                            @update:model-value="(value: any) => { if (column.type === 'integer') (props.row[column.field] = Math.round(value)) }"
                            @paste.prevent="onPaste($event, table.values, column.field, column.type, props.rowIndex)"
                          />
                          <QSelect
                            v-else-if="column.type === 'choice'"
                            v-model="props.row[column.field]"
                            :options="column.choices"
                            option-label="legend"
                            option-value="id"
                            emit-value
                            map-options
                            outlined
                            dense
                          />
                          <InputDate
                            v-else-if="column.type === 'date'"
                            v-model="props.row[column.field]"
                            :rules="isRequired(column)"
                            class="flex-1"
                            :disabled="['A', 'B'].includes(calculation?.step)"
                            @paste.prevent="onPaste($event, table.values, column.field, column.type, props.rowIndex)"
                            @update:model-value="props.row.is_extraconcursal = false"
                          />
                          <div v-else-if="column.type === 'boolean'" class="row justify-center">
                            <div
                              v-if="column.field === 'is_extraconcursal'"
                            >
                              <QToggle
                                v-if="props.row?.data_base >= calculation?.criterion?.dateRjRequest"
                                v-model="props.row[column.field]"
                                class="flex-1"
                                :disable="['A', 'B'].includes(calculation?.step)"
                              />
                            </div>
                            <QToggle
                              v-else
                              v-model="props.row[column.field]"
                              :disable="['A', 'B'].includes(calculation?.step)"
                              class="flex-1"
                            />
                          </div>
                        </div>
                      </QTd>
                    </QTr>
                  </template>
                  <template #bottom-row="props">
                    <QTr :props="props" class="bg--primary/3 color--primary font-bold">
                      <QTd v-for="column in props.cols as any[]" :key="column.id">
                        <div
                          v-if="table?.summary?.some(({ order }: any) => order === column.order)"
                          class="text-center"
                        >
                          <span v-if="getSummary(column.order, table.summary)?.label" class="mr-2">
                            {{ getSummary(column.order, table.summary).label }}
                          </span>
                          <span
                            v-if="getSummary(column.order, table.summary)?.key"
                          >
                            <span v-if="getSummary(column.order, table.summary)?.typeDisplay === 'text'">
                              {{ get(getSummary(column.order, table.summary).key, table.data) }}
                            </span>
                            <span v-if="getSummary(column.order, table.summary)?.typeDisplay === 'float'">
                              {{ formatNumber(
                                get(getSummary(column.order, table.summary).key, table.data),
                                getSummary(column.order, table.summary).decimals,
                              ) }}
                            </span>
                            <span v-if="getSummary(column.order, table.summary)?.typeDisplay === 'integer'">
                              {{ get(getSummary(column.order, table.summary).key, table.data) }}
                            </span>
                          </span>
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
                    {{ formatNumber((typeof credit?.total === 'number' ? credit?.total : credit?.total?.totalCorrected) || 0, 2) }}
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
                <Btn
                  label="Processar"
                  :disabled="['A', 'B'].includes(calculation?.step)"
                  @click="calculateCredit(credit, creditIndex)"
                />
              </div>
            </QForm>
          </Accordion>
        </div>
        <div v-else class="text-lg text-center">
          Nenhum Crédito listado para este Cálculo...
        </div>
      </QTabPanel>
      <QTabPanel name="ext">
        <AccountingStatement
          v-model="attrs.calculationId"
          :creditor="creditor"
          :recovering="recovering"
          :calculation-number="calculation?.number"
        />
      </QTabPanel>
    </QTabPanels>

    <template #out>
      <ChangeStatus
        v-model="showChangeStatus"
        :history="history"
        :options="options"
        :calculation="calculation"
        :status="calculation?.step"
        :special-approvers="project?.participants?.[3]?.[1]"
        @update-status="loadOptions(); loadCalculation()"
      />
      <NewCredit
        v-model="showNewCredit"
        :options="options"
        :rates="rates"
        :calculation-id="attrs.calculationId"
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
.credit-table tr:has(.has-error) {
  background-color: hsla(var(--error,0,0%,0%),0.05)
}
.credit-table td.q-td {
  padding: 8px 6px;
  width: 0.1%;
  white-space: nowrap;
}
.credit-table tr td:first-child {
  padding-left: 16px;
}
.credit-table tr td:last-child {
  padding-right: 8px;
}
.calculations-credits {
  background: transparent;
}
.calculations-credits .q-tab-panel {
padding: 0;
}
</style>
