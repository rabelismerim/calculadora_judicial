<script setup lang='ts'>
const attrs = useAttrs() as any

const { hasPermissions } = $user

const showUploadCreditors = $ref(false)
const showCreateCreditor = $ref(false)
let showUpdateCreditor = $ref(false)

let project = $ref({} as any)
let creditors = $ref([] as any[])
let rates = $ref([])
let creditorOptions = $ref({} as any)
const filterBy = $ref('')
let inactiveCreditors = $ref([] as any[])
const selectedTab = ref('ativos')
const tabs = $computed(() => [
  { label: `Ativos (${creditors?.length})`, value: 'ativos' },
  { label: `Inativos (${inactiveCreditors?.length})`, value: 'inativos' },
])

const nullCreditor = {
  name: '',
  legalNumber: '',
  recoverings: [],
}

let editingCreditor = $ref(clone(nullCreditor))
const clearCreditor = () => {
  editingCreditor = clone(nullCreditor)
}

const filteredCreditors = computed((): any[] => {
  const filtered: any[] = (!filterBy)
    ? creditors
    : creditors.filter((creditor: any) => {
      const {
        name,
        legalNumber,
        recovering: { name: recoveringName, legalNumber: recoveringLegalNuber } = {} as any,
      } = creditor
      const toCompare = [name, legalNumber, recoveringName, recoveringLegalNuber]
      return toCompare.some(item => item.toLocaleLowerCase().includes(filterBy.toLocaleLowerCase()))
    })
  return Object.values(filtered
    .reduce((accumulator: any, creditor: any) => {
      const newCreditor = clone(creditor)
      const { legalNumber } = creditor
      if (!newCreditor?.recoverings) {
        newCreditor.recoverings = []
        delete newCreditor.recovering
      }
      if (!accumulator[legalNumber]) {
        accumulator[legalNumber] = {
          ...newCreditor,
          legalNumber,
          recoverings: creditors
            .filter(({ recovering }: any) => recovering.creditorLegalNumber === legalNumber)
            .map(({ recovering }: any) => recovering),
        }
      }
      return accumulator
    }, {}))
})

const filteredInactiveCreditors = computed((): any[] =>
  inactiveCreditors.filter ((creditor: any) => creditor?.entity?.name
    .toLowerCase()
    .includes(filterBy.toLowerCase()),
  ),
)

const mapCreditor = (creditor: any) => {
  const {
    id,
    recoveringId,
    description,
    admission,
    dismissal,
    advocativeHours,
    fine,
    defaultInterest,
    occurrence,
    noticeAj,
    noticeRecovering,
    claimCreditor,
    claimLawyer,
    entity: { legalNumber, name },
  } = creditor
  const {
    entity: { name: recoveringName, legalNumber: recoveringLegalNuber },
  } = project?.recoverings?.find(({ id }: any) => recoveringId === id)
  return {
    id,
    name,
    legalNumber,
    description,
    admission,
    dismissal,
    advocativeHours,
    fine,
    defaultInterest,
    occurrence,
    recovering: {
      id: recoveringId,
      step: 1,
      open: false,
      name: recoveringName,
      legalNumber: recoveringLegalNuber,
      creditorLegalNumber: legalNumber,
      creditor: { ...creditor, legalNumber },
      creditorId: id,
      noticeAj,
      noticeRecovering,
      claimCreditor: claimCreditor.map((creditor: any) => ({ ...creditor, incidentId: creditor?.incident?.id })),
      claimLawyer,
    },
  }
}
let loadingCreditors = $ref(false)
const loadCreditors = async () => {
  loadingCreditors = true
  try {
    project = await projectService.getProject(attrs.projectId)
    const creditorsResult = await creditorsService.getCreditors(attrs.projectId)
    const mappedCreditors = []
    for (const creditor of creditorsResult) {
      mappedCreditors.push(mapCreditor(creditor))
      await delay(0.01)
    }
    creditors = mappedCreditors
  }
  catch (error) {
    printError('ERROR ON LOAD CREDITORS:', error)
  }
  finally {
    loadingCreditors = false
  }
}

const newCreditorOptions = computed(() => ({
  ocurrences: creditorOptions?.occurrenceOptions || [],
  recoverings: project?.recoverings || [],
  rates,
}))

const getOcurrence = (occurrenceId: string) => newCreditorOptions.value.ocurrences
  .find(({ id }: any) => id === occurrenceId)?.legend ?? occurrenceId
const mapInactiveCreditor = (creditor: any) => {
  const {
    recoveringId,
  } = creditor
  const recovering = newCreditorOptions.value?.recoverings?.find(({ id }: any) => recoveringId === id)
  return {
    ...creditor,
    recoveringName: recovering?.entity?.name,
    recoveringLegalNumber: recovering?.entity?.legalNumber,
  }
}
const {
  page: inactivePage,
  next: nextInactivePage,
  previous: previousInactivePage,
} = usePagination(computed(() => inactiveCreditors), 10)

let loadingInactiveCreditors = $ref(false)
const loadInactiveCreditors = async () => {
  loadingInactiveCreditors = true
  try {
    project = await projectService.getProject(attrs.projectId)
    const inactiveCreditorsResult = await creditorsService.getInactiveCreditors(attrs.projectId)
    const mappedInactiveCreditors = []
    for (const creditor of inactiveCreditorsResult) {
      mappedInactiveCreditors.push(mapInactiveCreditor(creditor))
      await delay(0.01)
    }
    inactiveCreditors = mappedInactiveCreditors
  }
  catch (error) {
    printError('ERROR ON LOAD CREDITORS:', error)
  }
  finally {
    loadingInactiveCreditors = false
  }
}

const selectAllInactiveCreditors = async () => {
  for (const creditor of inactiveCreditors) {
    creditor.toValidate = true
    await delay(0.01)
  }
}
const editCreditor = (creditor: any) => {
  const newCreditor = clone(creditor)
  const { legalNumber, recoverings } = newCreditor
  editingCreditor = {
    ...newCreditor,
    legalNumber: `${formatLegalNumber(legalNumber)} `,
    creditorsIds: recoverings.map(({ creditorId }: any) => creditorId),
  }
  showUpdateCreditor = true
}

const { dialog } = useQuasar()
let loadingValidate = $ref(false)
const validateCreditors = async () => {
  dialog({
    title: 'Validar Credores',
    message: 'Você tem certeza que deseja validar os credores marcados?',
    cancel: true,
    persistent: true,
  }).onOk(async () => {
    const toValidate = inactiveCreditors
      ?.map((creditor, index) => ({ ...creditor, isActive: true, index }))
      ?.filter(({ toValidate }: any) => toValidate) ?? []
    if (toValidate?.length <= 0) {
      throwError({ message: 'Não tem nenhum credor selecionado...' })
      return
    }
    loadingValidate = true
    try {
      for (const creditor of toValidate) {
        const { index } = creditor
        await creditorsService.updateCreditor(creditor)
        const newCreditor = mapCreditor(creditor)
        creditors.push(newCreditor)
        inactiveCreditors.splice(index, 1)
        await delay(0.01)
      }
    }
    catch (error) {
      printError('ERROR ON VALIDATE CREDITOR:', error)
    }
    finally {
      loadingValidate = false
    }
  })
}

let loadingOptions = $ref(false)
const loadOptions = async () => {
  loadingOptions = true
  try {
    rates = await ratesService.getRates()
    creditorOptions = await creditorsService.getOptions()
  }
  catch (error) {
    printError('ERROR ON LOAD CREDITORS OPTIONS:', error)
  }
  finally {
    loadingOptions = false
  }
}

const loading = $computed(() => loadingCreditors || loadingInactiveCreditors || loadingOptions || loadingValidate)

onMounted(() => {
  loadOptions()
  loadCreditors()
  loadInactiveCreditors()
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
    wrapper-classe="pb-0!"
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
          @click="loadCreditors();loadInactiveCreditors()"
        />
      </template>
    </Header>
    <TabFilter
      v-model:search="filterBy"
      v-model="selectedTab"
      :items="tabs"
      class="mb-0!"
    />

    <QTabPanels
      v-model="selectedTab"
    >
      <QTabPanel
        name="ativos"
        class="px-4 bg--background"
      >
        <div
          v-if="filteredCreditors.length > 0"
          class="grid gap-3"
        >
          <Accordion
            v-for="creditor in filteredCreditors"
            :key="creditor.legalManager + creditor.name"
            :title="creditor.name"
            :subtitle="formatLegalNumber(creditor.legalNumber)"
          >
            <div class="grid grid-cols-1 sm:grid-cols-2 px-7 py-5 border-b-1">
              <div class="sm:col-span-2">
                <b>Descrição:</b> {{ creditor.description || '-' }}
              </div>
            </div>

            <template #header-left>
              <IconHint
                icon="i-carbon-identification"
                hint="Este ícone indica que este\nitem é um Credor!"
                class="self-center"
              />
            </template>
            <template #header-right>
              <div class="flex-1 flex gap-2 justify-end items-center pl-8 pr-4">
                <Btn
                  v-if="hasPermissions('change_creditor')"
                  label="Editar Credor"
                  icon="i-carbon-edit"
                  transparent
                  @click.stop="editCreditor(creditor)"
                />
              </div>
            </template>
            <div v-if="creditor.recoverings.length > 0">
              <Accordion
                v-for="(recovering, index) in creditor.recoverings as any[]"
                :key="recovering.id"
                v-model="recovering.open"
                :title="recovering.name"
                :subtitle="formatLegalNumber(recovering.legalNumber)"
                class="pl-6 border-x-0 border-b-0 rounded-0"
                :class="{ 'border-t-0': index === 0 }"
              >
                <template #header-left>
                  <IconHint
                    icon="i-carbon-enterprise"
                    hint="Este ícone indica que este\nitem é uma Recuperanda!"
                    dark
                    class="self-center"
                  />
                </template>
                <QStepper
                  ref="stepper"
                  v-model="recovering.step"
                  color="primary"
                  animated
                  header-nav
                  flat
                  class="vertical border--primary border-1 mb-4 mr-3"
                >
                  <CreditorData
                    v-model="recovering.creditor"
                    :creditor-id="recovering.creditorId"
                    :options="creditorOptions"
                    :name="1"
                    title="Dados do Credor"
                    icon="o_request_page"
                    @save="loadCreditors"
                  />
                  <RecoveringNotice
                    v-model="recovering.noticeRecovering"
                    :creditor-id="recovering.creditorId"
                    :options="creditorOptions"
                    :name="2"
                    title="Edital Recuperanda"
                    icon="o_request_page"
                    @save="loadCreditors"
                  />
                  <AJNotice
                    v-model="recovering.noticeAj"
                    :creditor-id="recovering.creditorId"
                    :options="creditorOptions"
                    :name="3"
                    title="Edital AJ"
                    icon="o_request_page"
                    @save="loadCreditors"
                  />
                  <AdministrativeClaim
                    :model-value="recovering.claimCreditor.filter((claim: any) => !!claim?.isAdmin)"
                    :creditor-id="recovering.creditorId"
                    :options="creditorOptions"
                    :name="4"
                    title="Pleito Admnistrativo"
                    icon="o_attach_money"
                    @save="loadCreditors"
                  />
                  <JuridicalClaim
                    :model-value="recovering.claimCreditor.filter((claim: any) => !claim?.isAdmin)"
                    :creditor-id="recovering.creditorId"
                    :options="creditorOptions"
                    :name="5"
                    title="Pleito Jurídico"
                    icon="o_attach_money"
                    @save="loadCreditors"
                  />
                  <LawyerClaim
                    v-model="recovering.claimLawyer"
                    :creditor-id="recovering.creditorId"
                    :options="creditorOptions"
                    :name="6"
                    title="Pleito Advocatício"
                    icon="o_attach_money"
                    @save="loadCreditors"
                  />
                </QStepper>
              </Accordion>
            </div>
            <div v-else class="p-6 text-center">
              Nenhuma Recuperanda para esse Credor
            </div>
          </Accordion>
        </div>
        <div v-else class="text-lg text-center pt-5">
          Nenhum Credor para esse Projeto...
        </div>
      </QTabPanel>
      <QTabPanel
        name="inativos"
        class="px-4 bg--background"
      >
        <div
          v-if="inactiveCreditors?.length > 0"
          class="grid gap-3"
        >
          <Accordion
            v-for="creditor in inactivePage.items"
            :key="creditor.id"
            :title="creditor.entity.name"
            :subtitle="formatLegalNumber(creditor.entity.legalNumber)"
            @open="creditor.toValidate = true"
          >
            <div class="grid grid-cols-1 sm:grid-cols-2 px-7 py-5 border-b-1">
              <div><b>Nome:</b> {{ creditor?.entity?.name }}</div>
              <div v-if="isValidCPF(creditor?.legalNumber)">
                <b>Data de Admissão:</b> {{ formatDateFromBackend(creditor?.admission || '') || '-' }}
              </div>
              <div v-if="isValidCPF(creditor?.legalNumber)">
                <b>Data de Demissão:</b> {{ formatDateFromBackend(creditor?.dismissal || '') || '-' }}
              </div>
              <div><b>Multa:</b> {{ creditor.fine }}</div>
              <div><b>Horários Advocatícios:</b> {{ creditor.advocativeHours }}</div>
              <div><b>CPF/CNPJ:</b> {{ formatLegalNumber(creditor?.entity?.legalNumber || '') }}</div>
              <div><b>Juros Moratórios:</b> {{ creditor.defaultInterest }}</div>
              <div><b>Ocorrência:</b> {{ getOcurrence(creditor.occurrence) }}</div>
              <div class="sm:col-span-2">
                <b>Descrição:</b> {{ creditor.description }}
              </div>
            </div>
            <template #header-left>
              <IconHint
                icon="i-carbon-identification"
                hint="Este ícone indica que este\nitem é um Credor!"
                class="self-center"
              />
            </template>
            <template #header-right>
              <div class="flex-1 flex gap-2 justify-end items-center pl-8 pr-4">
                <QToggle v-model="creditor.toValidate" :false-value="null" />
              </div>
            </template>
            <div v-if="creditor.recoveringName" class="p-4 flex gap-4">
              <IconHint
                icon="i-carbon-enterprise"
                hint="Este ícone indica que este\nitem é uma Recuperanda!"
                dark
                class="self-center"
              />
              <div>
                <div class="text-lg font-bold">
                  {{ creditor.recoveringName }}
                </div>
                <div>{{ formatLegalNumber(creditor.recoveringLegalNumber) }}</div>
              </div>
            </div>
            <div v-else class="p-6 text-center">
              Nenhuma Recuperanda para esse Credor
            </div>
          </Accordion>
        </div>
        <div v-else class="pt-5 text-center">
          Parece que não existe nenhum usuário inativo no momento...
        </div>
      </QTabPanel>
    </QTabPanels>

    <div v-if="selectedTab === 'inativos' && inactiveCreditors?.length" class="flex justify-between px-4 sticky bottom-0 py-2 gap-4 bg--background">
      <div class="flex gap-4">
        <Btn
          label="Anterior"
          outlined
          @click.stop="previousInactivePage"
        />
        <Btn
          label="Próximo"
          outlined
          @click.stop="nextInactivePage"
        />
        {{ inactivePage.current }} de {{ inactivePage.total }}
      </div>
      <div class="flex gap-4">
        <Btn
          label="Selecionar Todos"
          outlined
          @click.stop="selectAllInactiveCreditors"
        />
        <Btn
          label="Validar Credores Selecionados"
          icon="i-carbon-checkmark"
          @click.stop="validateCreditors"
        />
      </div>
    </div>

    <template #out>
      <NewCreditor
        v-if="hasPermissions('add_creditor')"
        v-model="showCreateCreditor"
        :options="newCreditorOptions"
        @success="loadCreditors"
      />
      <UpdateCreditor
        v-if="hasPermissions('change_creditor')"
        v-model="showUpdateCreditor"
        v-model:creditor="editingCreditor"
        :options="newCreditorOptions"
        @success="loadCreditors"
        @clear="clearCreditor"
      />
      <UploadCreditors
        v-if="hasPermissions('add_creditor')"
        v-model="showUploadCreditors"
        :project-id="attrs.projectId"
      />
    </template>
  </Page>
</template>
