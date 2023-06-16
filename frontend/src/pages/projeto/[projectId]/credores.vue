<script setup lang='ts'>
const attrs = useAttrs() as any

let showModal = $ref(false)

let loading = $ref(false)
let project = $ref({} as any)
let creditors = $ref([] as any[])
let rates = $ref([])
let creditorOptions = $ref({} as any)
let editingCreditor = $ref({
  name: '',
  legalNumber: '',
  recoverings: [],
} as any)
const filterBy = $ref('')
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
      const { name, legalNumber } = creditor
      if (!creditor?.recoverings)
        creditor.recoverings = []
      if (!accumulator[legalNumber]) {
        accumulator[legalNumber] = {
          name,
          legalNumber,
          recoverings: creditors
            .filter(({ recovering }: any) => recovering.creditorLegalNumber === legalNumber)
            .map(({ recovering }: any) => recovering),
        }
      }
      return accumulator
    }, {}))
})
const creditorsCount = computed(() => filteredCreditors.value.length)
const loadCreditors = async () => {
  loading = true
  try {
    project = await projectService.getProject(attrs.projectId)
    const creditorsResult = await creditorsService.getCreditors(attrs.projectId)
    creditors = creditorsResult
      .map((creditor: any) => {
        const { id, recoveringId, entity: { legalNumber, name }, noticeAj, noticeRecovering, claimCreditor, claimLawyer } = creditor
        const { entity: { name: recoveringName, legalNumber: recoveringLegalNuber } } = project?.recoverings?.find(({ id }: any) => recoveringId === id)
        return {
          id,
          name,
          legalNumber,
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
const editCreditor = (creditor: any) => {
  const { id, entity: { name, legalNumber }, recoverings } = creditor
  editingCreditor = {
    id,
    name,
    legalNumber: `${formatLegalNumber(legalNumber)} `,
    recoverings: recoverings.map(({ id }: any) => id),
  }
  showModal = true
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

const newCreditorOptions = computed(() => ({
  recoverings: project?.recoverings || [],
  rates,
}))
onMounted(() => {
  loadOptions()
  loadCreditors()
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
          @click="showModal = true"
        />
      </div>
    </template>
    <Header :title="`Credores (${creditorsCount})`">
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Credores"
          @click="loadCreditors"
        />
      </template>
      <SearchFilter v-model="filterBy" />
    </Header>
    <div
      v-if="filteredCreditors.length > 0"
      class="grid gap-3"
    >
      <!-- <div v-for="creditor in filteredCreditors as any[]" :key="creditor.legalNumber">
        {{ creditor.name }} = {{ creditor.legalNumber }}
      </div> -->
      <Accordion
        v-for="creditor in filteredCreditors"
        :key="creditor.legalManager + creditor.name"
        :title="creditor.name"
        :subtitle="formatLegalNumber(creditor.legalNumber)"
      >
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
              disabled
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
              <CreditorClaim
                v-model="recovering.claimCreditor"
                :creditor-id="recovering.creditorId"
                :options="creditorOptions"
                :name="1"
                title="Pleito Credor"
                icon="o_attach_money"
                @save="loadCreditors"
              />
              <LawyerClaim
                v-model="recovering.claimLawyer"
                :creditor-id="recovering.creditorId"
                :options="creditorOptions"
                :name="2"
                title="Pleito Advocatício"
                icon="o_attach_money"
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
              <RecoveringNotice
                v-model="recovering.noticeRecovering"
                :creditor-id="recovering.creditorId"
                :options="creditorOptions"
                :name="4"
                title="Edital Recuperanda"
                icon="o_request_page"
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

    <template #out>
      <NewCreditor
        v-model="showModal"
        v-model:creditor="editingCreditor"
        :options="newCreditorOptions"
        @success="loadCreditors"
      />
    </template>
  </Page>
</template>
