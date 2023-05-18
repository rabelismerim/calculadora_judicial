<script setup lang='ts'>
const attrs = useAttrs() as any

let loading = $ref(false)

const menu = $ref('project')
const tab = $ref('cred')
const tabFilters = [
  { label: '1. Crédito', value: 'cred' },
  { label: '2. Extrato Contábil', value: 'ext' },
]

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
  options = await creditorsService.getOptions()
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
  const { funds = [], fundsIrrf = [], premisses = [] } = result
  result.credits = [...funds, ...fundsIrrf, ...premisses]
    .sort(({ createdAt: dateA }: any, { createdAt: dateB }: any) => dateA < dateB ? -1 : 1)
    .map((credit: any) => {
      credit.optionsTables = credit?.template?.tables.map(({ fields, description, endPoint, id, many }: any) => {
        const columns = fields
          ?.map(({ id, isEditable, key, label, order, required, typeDisplay }: any) =>
            ({
              id,
              isEditable,
              name: key,
              field: key,
              label,
              order,
              required,
              type: typeDisplay,
              align: (isEditable && typeDisplay !== 'boolean') ? 'left' : 'center',
            }))
          .sort(({ order: orderA }: any, { order: orderB }: any) => orderA < orderB ? -1 : 1)
        return { columns, description, endPoint, id, many, linesToAdd: 1 }
      })
      return credit
    })
  calculation = result
  if (showLoading)
    loading = false
}

const values = $ref([] as any[])
const addValues = (index: any, amount = 1) => {
  if (!values[index])
    values[index] = []
  values[index].push(...Array(amount).fill(0).map(() => clone({})))
}
addValues(0, 1)
addValues(1, 1)

const isRequired = ({ required }: any) => required && [(value: any) => !!value || 'Campo obrigatório!']

const filterInput = $ref('')
let templates = $ref([] as any[])
let newCredit = $ref({} as any)
const newCreditForm = ref(null as any)
let showNewCredit = $ref(false)
const filteredTemplates = computed(() => templates
  .filter(({ name }: any) => name.toLowerCase().includes(filterInput.toLowerCase())))
const clearNewCredit = () => {
  newCredit = {}
  newCreditForm.value.reset()
}
const loadTemplates = async () => {
  templates = await ratesService.getTemplates()
}
const loadTemplate = async (id: string) => {
  if (!id)
    return
  const result = await ratesService.getTemplate(id)
  newCredit.endPoint = result?.endPoint
  newCredit.fields = result?.fields?.map(({ id, key, label, order, required, typeDisplay }: any) => ({
    id,
    key,
    label,
    order,
    type: typeDisplay,
    required,
  }))
}
const host = import.meta.env.VITE_API_URL.slice(0, -9)
const createCredit = async () => {
  const { classId, coinId, rateId, templateId, endPoint } = newCredit
  loading = true
  try {
    if (!endPoint)
      return
    const result: any = await api.post(`${host}${endPoint}`, {
      ...newCredit,
      classes: {
        classe: classId,
      },
      coins: {
        coin: coinId,
      },
      rateId,
      templateId,
      calculationId: attrs.calculationId,
    })
      .then((result: any) => Object.values(result || {})[0] || {})
    loadCalculation()
    notify({ message: 'Crédito Criado com Sucesso!' })
    showNewCredit = false
    clearNewCredit()
  }
  catch (error) {
    printError('ERROR ON CREATING CREDIT:', error)
  }
  finally {
    loading = false
  }
}

const creditsAmount = computed(() => calculation?.credits?.length || 0)
const classesAmount = computed(() => calculation?.classes?.length)
const totalValue = computed(() => calculation?.funds
  ?.flatMap(({ calculations }: any) => calculations?.map(({ updatedValue }: any) => updatedValue))
  ?.reduce((acc: number, curr: number) => acc + curr || 0, 0))
onMounted(async () => {
  loading = true
  try {
    await loadProject()
    await loadCreditor()
    await loadCalculation()
    await loadTemplates()
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

const calculate = async () => {
  const headers: any = {
    'Content-type': 'application/json',
    'Accept': 'application/json',
  }
  if (import.meta.env.VITE_TOKEN)
    headers.Authorization = `Token ${import.meta.env.VITE_TOKEN}`
  const endpoints = calculation?.credits?.[0]?.template?.tables?.map(({ endPoint }: any) => endPoint)
  loading = true
  for (const index in endpoints) {
    for (const lineIndex in values[index as any]) {
      const line = values[index as any][lineIndex]
      if (Object.keys(line).length === 0)
        break
      const result: any = await fetch(`${host}${endpoints[index]}`, {
        method: 'POST',
        body: JSON.stringify({ ...line, fund_id: calculation?.funds?.[0]?.id }),
        headers,
      })
        .then(response => response.json())
      values[index as any][lineIndex] = Object.values(result)?.[0]
    }
  }
  loading = false
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
      <QTabPanels v-model="menu" animated class="calculation-details">
        <QTabPanel name="project" class="px-0">
          <ProjectDescription :project="project" />
        </QTabPanel>
        <QTabPanel name="analysis" class="px-0">
          <ProjectDetailCell label="Id">
            {{ `#${calculation?.number}` || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell label="Incidente">
            {{ calculation?.incident?.number || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell label="Recuperanda">
            {{ recovering?.entity?.name || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell label="Recuperanda - CNPJ">
            {{ formatLegalNumber(recovering?.entity?.legalNumber) || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell label="Credor">
            {{ creditor?.entity?.name || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell :label="`Credor - ${creditor?.entity?.legalNumber?.length === 11 ? 'CPF' : 'CNPJ'}`">
            {{ formatLegalNumber(creditor?.entity?.legalNumber) || '-' }}
          </ProjectDetailCell>
          <ProjectDetailCell label="Classes">
            <div
              v-for="classe in calculation?.classes as any[]"
              :key="classe.id"
            >
              {{ classe.classeDisplay }}: {{ classe.totalValue }}%
            </div>
          </ProjectDetailCell>
        </QTabPanel>
      </QTabPanels>
    </template>
    <Header
      :title="`Cálculo #${calculation?.number || ''} - ${calculation?.creditor?.entity?.name || ''}`"
    >
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Créditos"
          @click="loadCalculation(true)"
        />
      </template>
      <Btn label="Novo Crédito" icon="i-carbon-add-filled" @click="showNewCredit = true" />
    </Header>

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
          {{ totalValue?.toLocaleString('pt-BR', { style: 'currency', currency: 'BRL' }) }}
        </div>
      </GraphCard>
    </div>

    <div v-if="calculation?.credits?.length > 0" class="flex gap-4">
      <Accordion
        v-for="(credit, index) in calculation?.credits as any[]"
        :key="index"
        :title="`Crédito ${credit?.template?.name}`"
        :subtitle="credit.name"
        class="rounded-0"
      >
        <template #header-right>
          <div class="flex gap-2 self-center">
            <Btn
              label="Editar Crédito"
              icon="i-carbon-edit"
              transparent
              @click.stop
            />
            <Btn
              label="Excluir Crédito"
              icon="i-carbon-trash-can"
              transparent
              @click.stop
            />
          </div>
        </template>
        <QForm @submit.prevent>
          <div
            v-for="(table, index) in credit?.optionsTables as any[]"
            :key="table.id"
            class="p-4"
          >
            <div class="text-lg font-bold mb-2 flex justify-between items-center">
              <div>{{ table.description }}</div>
              <AddLines
                v-model="table.linesToAdd"
                @add-lines="addValues(index, table.linesToAdd)"
              />
            </div>
            <QTable
              :rows="values[index]"
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
                    <div class="flex justify-center items-center">
                      <div v-if="!column.isEditable" class="row justify-center">
                        {{ props.row[column.field] }}
                      </div>
                      <QInput
                        v-else-if="column.type === 'text'"
                        v-model="props.row[column.field]"
                        :rules="isRequired(column)"
                        class="flex-1"
                        outlined
                        dense
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
                      />
                      <InputDate
                        v-else-if="column.type === 'date'"
                        v-model="props.row[column.field]"
                        :rules="isRequired(column)"
                        class="flex-1"
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
              <div>Quantidade de Créditos: 0</div>
              <div>Total dos Valores: R$ 0</div>
            </div>
            <div>
              <div>Calculados com Sucesso: 0</div>
              <div>Calculados com Error: 0</div>
            </div>
            <Btn label="Calcular" @click="calculate(index)" />
          </div>
        </QForm>
      </Accordion>
    </div>
    <div v-else class="text-lg text-center">
      Nenhum Crédito listado para este Cálculo...
    </div>
    <template #out>
      <Modal
        v-model="showNewCredit"
        title="Criar Novo Credito"
        hint="Vincular um Novo Crédito à este Cálculo."
        modal-class="max-w-200"
        @close="clearNewCredit"
      >
        <QForm ref="newCreditForm" @submit.prevent="createCredit">
          <div class="p-4 grid grid-cols-2 gap-x-4">
            <QSelect
              v-model="newCredit.templateId"
              :options="filteredTemplates"
              label="Tipo"
              outlined
              use-input
              emit-value
              map-options
              option-value="id"
              option-label="name"
              :disable="loading"
              :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
              dense
              @input-value="(value: string) => filterInput = value"
              @update:model-value="(value: string) => loadTemplate(value)"
            />
            <QSelect
              v-model="newCredit.classId"
              :options="options?.classesOptions"
              label="Classe"
              outlined
              emit-value
              map-options
              option-value="id"
              option-label="legend"
              :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
              :disable="loading"
              dense
            />
            <QSelect
              v-model="newCredit.coinId"
              :options="options?.coinOptions"
              label="Moeda"
              outlined
              emit-value
              map-options
              option-value="id"
              option-label="legend"
              :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
              :disable="loading"
              dense
            />
            <QSelect
              v-model="newCredit.rateId"
              :options="rates"
              label="Taxa"
              outlined
              emit-value
              map-options
              option-value="id"
              option-label="index"
              :disable="loading"
              :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
              dense
            />
            <div v-for="field in newCredit?.fields as any[]" :key="field.id">
              <QInput
                v-if="field.type === 'text'"
                v-model="newCredit[field.key]"
                :label="field.label"
                :rules="isRequired(field)"
                outlined
                dense
              />
              <QInput
                v-else-if="field.type === 'float' || field.type === 'integer'"
                v-model="newCredit[field.key]"
                :label="field.label"
                :rules="isRequired(field)"
                type="number"
                :step="field.type === 'float' ? 'any' : 1"
                outlined
                dense
                @update:model-value="(value: number | string | null) => (field.type === 'integer') && (newCredit[field.key] = Math.round(value as number))"
              />
              <QToggle
                v-else-if="field.type === 'boolean'"
                v-model="newCredit[field.key]"
                :label="field.label"
                left-label
              />
              <InputDate
                v-else-if="field.type === 'date'"
                v-model="newCredit[field.key]"
                :rules="isRequired(field)"
                :label="field.label"
                dense
              />
              <div v-else>
                {{ field.label }} - {{ field.key }} - {{ field.type }}
              </div>
            </div>
          </div>
          <div class="border-1 border-t-black/12 p-4 flex justify-end relative">
            <QLinearProgress
              v-if="loading"
              indeterminate
              color="secondary"
              class="absolute top-0 left-0"
              size="xs"
            />
            <Btn
              type="submit"
              label="Criar Crédito"
              :loading="loading"
              loading-label="Criando Crédito..."
            />
          </div>
        </QForm>
      </Modal>
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
</style>
