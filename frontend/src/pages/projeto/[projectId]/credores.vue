<script setup lang='ts'>
const attrs = useAttrs() as any

const showCreateCreditor = $ref(false)
let showUpdateCreditor = $ref(false)

let loading = $ref(false)
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

const creditorsCount = computed(() => filteredCreditors.value.length)
const loadCreditors = async () => {
  loading = true
  try {
    project = await projectService.getProject(attrs.projectId)
    const creditorsResult = await creditorsService.getCreditors(attrs.projectId)
    creditors = creditorsResult
      .map((creditor: any) => {
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
            creditorId: id,
            noticeAj,
            noticeRecovering,
            claimCreditor,
            claimLawyer,
          },
        }
      })
  }
  catch (error) {
    printError('ERROR ON LOAD CREDITORS:', error)
  }
  finally {
    loading = false
  }
}

const newCreditorOptions = computed(() => ({
  ocurrences: creditorOptions?.occurrenceOptions || [],
  recoverings: project?.recoverings || [],
  rates,
}))
const loadInactiveCreditors = async () => {
  loading = true
  try {
    project = await projectService.getProject(attrs.projectId)
    const inactiveCreditorsResult = await validationService.getInactive(attrs.projectId)
    inactiveCreditors = inactiveCreditorsResult
      .map((creditor: any) => {
        const {
          recoveringId,
        } = creditor
        const recovering = newCreditorOptions.value?.recoverings?.find(({ id }: any) => recoveringId === id)
        return {
          ...creditor,
          recoveringName: recovering?.entity?.name,
          recoveringLegalNumber: recovering?.entity?.legalNumber,
        }
      })
  }
  catch (error) {
    printError('ERROR ON LOAD CREDITORS:', error)
  }
  finally {
    loading = false
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

const validateCreditor = async (creditor: any) => {
  if (creditor) {
    const newCreditor = clone(creditor)
    const { legalNumber, recoverings } = newCreditor
    editingCreditor = {
      ...newCreditor,
      legalNumber: `${formatLegalNumber(legalNumber)} `,
      creditorsIds: recoverings?.map(({ creditorId }: any) => creditorId),
    }
    try {
      await creditorsService.updateCreditor(newCreditor, true)

      inactiveCreditors = inactiveCreditors.filter(c => c.id !== newCreditor.id)

      creditors.push(newCreditor)
    }
    catch (error) {
      console.error('ERROR ON VALIDATE CREDITOR:', error)
    }
  }

  showUpdateCreditor = true
}

const loadOptions = async () => {
  try {
    rates = await ratesService.getRates()
    creditorOptions = await creditorsService.getOptions()
  }
  catch (error) {
    printError('ERROR ON LOAD CREDITORS OPTIONS:', error)
  }
}

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
  >
    <template #header>
      <div class="flex-1 flex justify-end">
        <Btn
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
      <!-- <SearchFilter v-model="filterBy" /> -->
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
              <div><b>Nome:</b> {{ creditor.name }}</div>
              <div><b>Multa:</b> {{ creditor.fine }}</div>
              <div><b>Horários Advocatícios:</b> {{ creditor.advocativeHours }}</div>
              <div><b>CPF/CNPJ:</b> {{ creditor.legalNumber }}</div>
              <div><b>Juros Moratórios:</b> {{ creditor.defaultInterest }}</div>
              <div><b>Ocorrência:</b> {{ creditor.occurrence }}</div>
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
                <Btn
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
                <template #header-right>
                  <div class="flex-1 flex items-center pl-8" />
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
                    :model-value="creditor"
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
                  <CreditorClaim
                    v-model="recovering.claimCreditor"
                    :creditor-id="recovering.creditorId"
                    :options="creditorOptions"
                    :name="4"
                    title="Pleito Credor"
                    icon="o_attach_money"
                    @save="loadCreditors"
                  />
                  <LawyerClaim
                    v-model="recovering.claimLawyer"
                    :creditor-id="recovering.creditorId"
                    :options="creditorOptions"
                    :name="5"
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
            v-for="creditor in filteredInactiveCreditors"
            :key="creditor.id"
            :title="creditor.entity.name"
            :subtitle="formatLegalNumber(creditor.entity.legalNumber)"
          >
            <div class="grid grid-cols-1 sm:grid-cols-2 px-7 py-5 border-b-1">
              <div><b>Nome:</b> {{ creditor?.entity?.name }}</div>
              <div><b>Multa:</b> {{ creditor.fine }}</div>
              <div><b>Horários Advocatícios:</b> {{ creditor.advocativeHours }}</div>
              <div><b>CPF/CNPJ:</b> {{ creditor?.entity?.legalNumber }}</div>
              <div><b>Juros Moratórios:</b> {{ creditor.defaultInterest }}</div>
              <div><b>Ocorrência:</b> {{ creditor.occurrence }}</div>
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
                <Btn
                  label="Validar Credor"
                  icon="i-carbon-checkmark"
                  transparent
                  @click.stop="validateCreditor(creditor)"
                />
              </div>
            </template>
            <div v-if="inactiveCreditors?.length > 0">
              <Accordion
                v-for="(creditor, index) in inactiveCreditors as any[]"
                :key="creditor.id"

                :title="creditor.recoveringName"
                :subtitle="formatLegalNumber(creditor.recoveringLegalNumber)"
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
              </Accordion>
            </div>
            <div v-else class="p-6 text-center">
              Nenhuma Recuperanda para esse Credor
            </div>
          </Accordion>
        </div>
      </QTabPanel>
    </QTabPanels>

    <template #out>
      <NewCreditor
        v-model="showCreateCreditor"
        :options="newCreditorOptions"
        @success="loadCreditors"
      />
      <UpdateCreditor
        v-model="showUpdateCreditor"
        v-model:creditor="editingCreditor"
        :options="newCreditorOptions"
        @success="loadCreditors"
        @clear="clearCreditor"
      />
    </template>
  </Page>
</template>
