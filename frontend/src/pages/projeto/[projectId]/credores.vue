<script setup lang='ts'>
const attrs = useAttrs() as any

const { hasPermissions } = $user

const nullPagination = {
  sortBy: 'name',
  descending: false,
  page: 1,
  rowsPerPage: 5,
  rowsNumber: 5,
  filterBy: '',
  filterColumn: 'name',
}

const showUploadCreditors = $ref(false)
const showCreateCreditor = $ref(false)
let showUpdateCreditor = $ref(false)

let project = $ref({} as any)
let rates = $ref([] as any[])
let creditorOptions = $ref({} as any)
const expandedCreditor = $ref('')

const nullCreditor = {
  name: '',
  legalNumber: '',
  recovering: {
    loading: false,
  },
}

let editingCreditor = $ref(clone(nullCreditor))
const clearCreditor = () => {
  editingCreditor = clone(nullCreditor)
}

const mapCreditor = (recovering: any) => (creditor: any) => {
  const {
    entity: { legalNumber = '', name = '' } = {},
    claimCreditor = [],
  } = creditor ?? {}
  recovering.loading = false

  return {
    ...creditor,
    name,
    legalNumber,
    recovering,
    claimCreditor: claimCreditor.map((creditor: any) => ({ ...creditor, incidentId: creditor?.incident?.id })),
  }
}

let loadingProject = $ref(false)
const loadProject = async () => {
  loadingProject = true
  try {
    const result = await projectService.getProject(attrs.projectId)
    project = {
      ...result,
      recoverings: result?.recoverings?.map((recovering: any) => ({
        ...recovering,
        open: false,
        loading: false,
        pagination: { ...nullPagination },
        creditors: [],
        step: 1,
      })),
    }
  }
  catch (error) {
    printError(`ERROR ON LOAD PROJECT ${attrs.projectId}:`, error)
  }
  finally {
    loadingProject = false
  }
}

const creditorColumns = [
  {
    name: 'icon',
    field: 'icon',
  },
  {
    name: 'entity__name',
    field: 'entity',
    label: 'Credor',
    align: 'left',
    classes: 'w-25',
    sortable: true,
    format: value => value?.name ?? '-',
  },
  {
    name: 'entity__legal_number',
    field: 'entity',
    label: 'CPF/CNPJ',
    align: 'left',
    classes: 'w-25',
    sortable: true,
    format: value => formatLegalNumber(value?.legalNumber),
  },
  {
    name: 'person_type',
    field: 'personType',
    label: 'Tipo',
    align: 'left',
    classes: 'w-25',
    sortable: true,
    format: value => value ?? '-',
  },
  {
    name: 'action',
    field: 'action',
    label: 'Ação',
    headerClasses: 'pr-24!',
  },
] as {
  name: string
  label: string
  field: string
  classes?: string
  headerClasses?: string
  required?: boolean
  align?: 'left' | 'right' | 'center'
  sortable?: boolean
  format?: (val: any, row: any) => any
}[]

const loadCreditors = async (recovering: any, props: any = {}) => {
  if (!recovering)
    return
  recovering.loading = true
  const localPagination = {
    ...nullPagination,
    ...recovering.pagination,
    ...props.pagination,
  }
  try {
    const { items, count: rowsNumber } = await creditorsService.getCreditorsByLegalNumber(attrs.projectId, recovering?.entity?.legalNumber, localPagination)
    recovering.creditors = items.map(mapCreditor(recovering))
    recovering.pagination = {
      ...localPagination,
      rowsNumber,
    }
  }
  catch (error) {
    printError(`ERROR ON LOADING RECOVERING ${formatLegalNumber(recovering.entity?.legalNumber)}`, error)
  }
  finally {
    recovering.loading = false
  }
}
const newCreditorOptions = computed(() => ({
  ocurrences: creditorOptions?.occurrenceOptions || [],
  recoverings: project?.recoverings || [],
  rates,
}))

const editCreditor = (creditor: any) => {
  if (!creditor?.id)
    return
  const { entity: { name = '', legalNumber = '' } = {} } = creditor ?? {}
  editingCreditor = {
    ...creditor,
    name,
    legalNumber: formatLegalNumber(legalNumber),
  }
  showUpdateCreditor = true
}

let loadingOptions = $ref(false)
const loadOptions = async () => {
  loadingOptions = true
  try {
    const result = await ratesService.getRates()
    rates = result as unknown as any[]
    creditorOptions = await creditorsService.getOptions()
  }
  catch (error) {
    printError('ERROR ON LOAD CREDITORS OPTIONS:', error)
  }
  finally {
    loadingOptions = false
  }
}

const loading = $computed(() => loadingProject || loadingOptions)

onMounted(async () => {
  loadOptions()
  await loadProject()
})
</script>

<template>
  <Page
    :loading="loading"
    :links="[
      { label: 'Projetos', url: '/projetos' },
      { label: project.description, url: `/projeto/${attrs.projectId}` },
      { label: 'Credores' },
    ]"
    class="flex flex-col flex-1"
    wrapper-classe="pb-8!"
  >
    <template #header>
      <div class="flex-1 flex justify-end gap-4">
        <Btn
          v-if="hasPermissions('add_creditor')"
          label="Carregar Credores"
          icon="i-carbon-upload"
          outlined
          @click="showUploadCreditors = true"
        />
        <Btn
          v-if="hasPermissions('add_creditor')"
          label="Novo Credor"
          icon="i-carbon-add-filled"
          @click="showCreateCreditor = true"
        />
      </div>
    </template>
    <Header title="Credores">
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Credores"
          @click="loadProject"
        />
      </template>
    </Header>

    <div v-if="project?.recoverings?.length > 0" class="flex flex-col gap-3">
      <Accordion
        v-for="recovering in project?.recoverings ?? []"
        :key="recovering.id"
        v-model="recovering.open"
        :title="recovering.entity?.name"
        :subtitle="formatLegalNumber(recovering.entity.legalNumber)"
        class="accordion w-[min(1600px,100%)_!important]"
        @open="loadCreditors(recovering)"
      >
        <template #header-left>
          <IconHint
            icon="i-carbon-enterprise"
            hint="Este ícone indica que este\nitem é uma Recuperanda!"
            dark
            class="self-center"
          />
        </template>
        <template #header-right>
          <div class="flex-1 flex gap-2 justify-end items-center pl-4 pr-4">
            <!-- <div class="font-bold flex no-wrap items-center gap-2 text-lg">
              Total: R$ {{ formatNumber(recovering?.total || 0, 2) }}
              <Hint value="Total dos Cálculos Aprovados." />
            </div> -->
            <SearchFilter
              v-if="recovering.open"
              v-model:search="recovering.pagination.filterBy"
              v-model:field="recovering.pagination.filterColumn"
              :options="{
                name: 'Nome do Credor',
                cpf_cnpj: 'CPF/CNPJ do Credor',
              }"
              @update:search="loadCreditors(recovering)"
            />
          </div>
        </template>

        <QTable
          v-model:pagination="recovering.pagination"
          :loading="recovering.loading"
          :columns="creditorColumns"
          :rows="recovering.creditors"
          :rows-per-page-options="[5, 10, 15, 20, 25]"
          no-data-label="Nenhum Credor cadastrado para essa Recuperanda"
          row-key="id"
          flat
          @request="props => loadCreditors(recovering, props)"
        >
          <template #header="props">
            <QTr :props="props">
              <QTh
                v-for="col in props.cols"
                :key="col.name"
                :props="props"
                :auto-width="col.name === 'icon'"
              >
                {{ col.label }}
              </QTh>
            </QTr>
          </template>
          <template #body="props">
            <QTr
              :props="props"
              class="cursor-pointer"
              @click="expandedCreditor = !expandedCreditor || expandedCreditor !== props.row?.id ? expandedCreditor = props.row?.id : ''"
            >
              <QTd
                v-for="col in props.cols"
                :key="col.name"
                :props="props"
                :auto-width="col.name === 'icon'"
              >
                <div class="flex justify-end gap-3">
                  <Btn
                    v-if="col.name === 'action'"
                    label="Editar Credor"
                    icon="i-carbon-edit"
                    transparent
                    @click.stop="editCreditor(props.row)"
                  />
                </div>
                <div
                  v-if="col.name === 'icon'"
                  :class="{ 'rotate-180': props.row?.id === expandedCreditor }"
                  class="group h-8 w-8 rounded-8 text--secondary text-5 flex justify-center items-center hover:bg--secondary/20 tween-600"
                >
                  <div class="i-carbon-chevron-down" />
                </div>
                <span v-else>{{ col.value }}</span>
              </QTd>
            </QTr>
            <QTr v-show="expandedCreditor === props.row?.id" :props="props">
              <QTd colspan="100%" class="p-0!">
                <QStepper
                  ref="stepper"
                  v-model="recovering.step"
                  color="primary"
                  animated
                  header-nav
                  flat
                  class="vertical border--primary border-1 rounded-0!"
                >
                  <CreditorData
                    v-model:creditor="props.row"
                    :options="creditorOptions"
                    :name="1"
                    title="Dados do Credor"
                    icon="o_request_page"
                    @save="loadCreditors(recovering)"
                  />
                  <RecoveringNotice
                    v-model="props.row.noticeRecovering"
                    :creditor-id="props.row.id"
                    :options="creditorOptions"
                    :name="2"
                    title="Edital Recuperanda"
                    icon="o_request_page"
                    @save="loadCreditors(recovering)"
                  />
                  <AJNotice
                    v-model="props.row.noticeAj"
                    :creditor-id="props.row.id"
                    :options="creditorOptions"
                    :name="3"
                    title="Edital AJ"
                    icon="o_request_page"
                    @save="loadCreditors(recovering)"
                  />
                  <AdministrativeClaim
                    :model-value="props.row.claimCreditor?.filter((claim: any) => !!claim?.isAdmin)"
                    :creditor-id="props.row.id"
                    :options="creditorOptions"
                    :name="4"
                    title="Pleito Admnistrativo"
                    icon="o_attach_money"
                    @save="loadCreditors(recovering)"
                  />
                  <JuridicalClaim
                    :model-value="props.row.claimCreditor?.filter((claim: any) => !claim?.isAdmin)"
                    :creditor-id="props.row.id"
                    :options="creditorOptions"
                    :name="5"
                    title="Pleito Jurídico"
                    icon="o_attach_money"
                    @save="loadCreditors(recovering)"
                  />
                  <LawyerClaim
                    v-model="props.row.claimLawyer"
                    :creditor-id="props.row.id"
                    :options="creditorOptions"
                    :name="6"
                    title="Pleito Advocatício"
                    icon="o_attach_money"
                    @save="loadCreditors(recovering)"
                  />
                </QStepper>
              </QTd>
            </QTr>
          </template>
        </QTable>
      </Accordion>
    </div>
    <div v-else class="text-lg text-center pt-5">
      Nenhum Credor nessa listagem...
    </div>

    <template #out>
      <NewCreditor
        v-if="hasPermissions('add_creditor')"
        v-model="showCreateCreditor"
        :options="newCreditorOptions"
        @success="loadCreditors(editingCreditor.recovering)"
      />
      <UpdateCreditor
        v-if="hasPermissions('change_creditor')"
        v-model="showUpdateCreditor"
        v-model:creditor="editingCreditor"
        v-model:loading="editingCreditor.recovering.loading"
        :options="newCreditorOptions"
        @clear="clearCreditor"
        @success="loadCreditors(editingCreditor.recovering)"
      />
      <UploadCreditors
        v-if="hasPermissions('add_creditor')"
        v-model="showUploadCreditors"
        :project-id="attrs.projectId"
      />
    </template>
  </Page>
</template>
