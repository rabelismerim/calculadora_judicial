<script setup lang="ts">
const attrs = useAttrs() as any
const router = useRouter()

let loading = $ref(false)
const filterBy = $ref('')
const sideOpen = $ref(true)
const showTime = $ref(false)
const tab = $ref('all')
let project: any = $ref({})
let users: any = $ref([])

const filteredRecoverings = computed(() => {
  if (tab === 'all')
    return project?.recoverings || []
  return project?.recoverings?.filter(() => false)
})

const time = computed(() => {
  const { projectUsers = [] } = project
  return projectUsers.reduce((acc: any, current: any) => {
    const { firstName, lastName, username, userpicture, groups } = current
    const user = {
      picture: userpicture,
      fullName: `${firstName} ${lastName}`,
      email: `${username}@deloitte.com`,
    }
    groups.forEach(({ name }: any) => {
      if (!acc[name])
        acc[name] = []
      acc[name].push(user)
    })
    return acc
  }, {})
})

const loadProject = async () => {
  loading = true
  try {
    users = await usersService.getUsers()
    project = await projectService.getProject(attrs.id)
  }
  catch (error) {
    printError(`ERROR ON LOAD PROJECT ${attrs.id}:`, error)
  }
  finally {
    loading = false
  }
}
onMounted(() => {
  loadProject()
})
</script>

<template>
  <div class="relative flex flex-1 justify-center">
    <QLinearProgress
      v-if="loading"
      indeterminate
      color="secondary"
      class="absolute top-0 left-0 z-1"
      size="md"
    />
    <div
      class="relative flex-1 grid lg:grid-cols-[320px_1fr] tween-800"
      :class="{ 'lg:-translate-x-284px lg:w-[calc(100vw+284px)]': !sideOpen }"
    >
      <div
        class="fixed z-10 inset-block-0 pt-14 pb-10 left-0 max-w-80  lg:py-0 lg:relative bg--base pb-0 border-r-1 border-black/12 tween-800"
        :class="{ '-translate-x-284px lg:translate-0': !sideOpen }"
      >
        <div class="relative pr-9 h-full max-h-[calc(100vh-96px)] overflow-x-hidden overflow-y-auto scroll-left">
          <div class="p-8 pr-0">
            <h2 class="font-bold text-2xl bg--base sticky top-0 py-4">
              Informações Principais
            </h2>
            <div>
              <ProjectDetailCell label="Engagement">
                <div v-for="engagement in project?.engagement?.numbers" :key="engagement">
                  {{ engagement }}
                </div>
              </ProjectDetailCell>

              <ProjectDetailCell label="Sócio Jurídico">
                {{ project?.legalPartner?.fullName || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Sócio Financeiro">
                {{ project?.financialPartner?.fullName || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Gerente Jurídico">
                {{ project?.legalManager?.fullName || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Gerente Financeiro">
                {{ project?.financialManager?.fullName || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Gerente de Cálculo">
                {{ project?.calculationManager?.fullName || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Recuperandas">
                <div
                  v-for="recovering in project?.recoverings"
                  :key="recovering.id"
                  class="mb-2"
                >
                  <div class="font-bold">
                    {{ recovering.entity.name }}
                  </div>
                  <div>{{ formatLegalNumber(recovering.entity.legalNumber) }}</div>
                </div>
              </ProjectDetailCell>

              <ProjectDetailCell label="Data de Pedido de Recuperação">
                {{ formatDateFromBackend(project?.projectStart) || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Número do Processo Principal">
                {{ project?.processNumber || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Juiz">
                {{ toProperName(project?.judge?.description || '') || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Advogado">
                {{ toProperName(project?.lawyer?.description || '') || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Comarca">
                {{ project?.region?.description || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Vara">
                {{ project?.court?.description || '-' }}
              </ProjectDetailCell>
            </div>
          </div>
          <div
            class="absolute right-0 top-0 bottom-0 p-1 flex cursor-pointer"
            @click="sideOpen = !sideOpen"
          >
            <div class="hover:bg--secondary/15 pt-7 flex-1 flex flex-col items-center gap-4 rounded-2 tween">
              <div class="i-carbon-chevron-right text-lg tween-800" :class="{ 'rotate-180': sideOpen }" />
              <div class="text-vertical whitespace-nowrap font-bold text-lg tween-800" :class="{ 'opacity-0': sideOpen }">
                Informações Principais
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="pr-8 py-8 pl-16 lg:pl-8 max-h-[calc(100vh-96px)] overflow-y-auto overflow-x-hidden flex justify-center">
        <div class="max-w-[min(1600px,100%)]">
          <div class="flex gap-8 items-center mb-8">
            <button
              class="group flex gap-1 items-center uppercase font-semibold hover:text--secondary tween-800 z-1"
              @click="router.push({ path: '/projetos' })"
            >
              <div class="i-carbon-chevron-left group-hover:-translate-x-1 tween-800" />
              Voltar
            </button>

            <Breadcrumbs :links="[{ label: 'Projetos', url: '/projetos' }, { label: project.description }]" />
          </div>

          <div class="mb-8 flex justify-between gap-4">
            <h1 class="font-bold text-4xl">
              Projeto {{ project.description }}
            </h1>
            <div class="flex gap-2">
              <Btn
                label="Participantes"
                icon="i-carbon-events"
                outlined
                @click="showTime = true"
              />
              <Btn
                label="Editar"
                icon="i-carbon-edit"
                disabled
              />
            </div>
          </div>

          <div class="grid grid-cols-3 grid-rows-2 gap-6 mb-8">
            <GraphGauge
              :values="[]"
              title="Quantidade de Cálculos por Status"
              hint="Esse gráfico apresenta a quantidade de Cálculos para cada status."
              class="row-span-2"
            />
            <GraphCard
              title="Quantidade Total de Credores"
              hint="O Número total dos Credores deste Projeto."
            >
              <div class="font-bold text-5xl flex-1 flex items-center">
                0
              </div>
            </GraphCard>
            <GraphCard
              title="Valor Total dos Credores"
              hint="Somatório dos Cálculos aprovados de todos os Credores."
            >
              <div class="font-bold text-5xl flex-1 flex items-center">
                R$ 0 mil
              </div>
            </GraphCard>
            <ProgressList
              :values="[]"
              title="Quantidade de Cálculos por Classe"
              hint="Classes na Recuperação Judicial:\n  • Classe I - Créditos Trabalhistas\n  • Classe II - Créditos com Garantia Real\n  • Classe III - Créditos Quirográficos\n  • Classe IV - Créditos enquadrados como Microempresa ou Empresa de pequeno porte."
            />
            <ProgressList
              :values="[]"
              title="Valores dos Cálculos por Classe (mil R$)"
              hint="Classes na Recuperação Judicial:\n  • Classe I - Créditos Trabalhistas\n  • Classe II - Créditos com Garantia Real\n  • Classe III - Créditos Quirográficos\n  • Classe IV - Créditos enquadrados como Microempresa ou Empresa de pequeno porte."
            />
          </div>

          <div class="mb-8 flex justify-between gap-4">
            <div class="flex gap-2 no-wrap items-center">
              <h1 class="font-bold text-4xl">
                Cálculos
              </h1>
              <ReloadBtn
                hint="Recarregar a Lista de Cálculos"
                @click="loadProject"
              />
            </div>
            <div class="flex gap-2">
              <Btn
                label="Exportar Cálculos Válidos"
                icon="i-carbon-document-export"
                disabled
              />
            </div>
          </div>

          <div class="mb-4 border-b-2 boder-black/12 flex justify-between items-center">
            <q-tabs
              v-model="tab"
              class=""
              align="left"
              active-color="secondary"
            >
              <q-tab name="all" label="Todos" />
              <q-tab name="d" label="A revisar" />
              <q-tab name="c" label="A aprovar" />
              <q-tab name="p" label="Aprovado" />
            </q-tabs>
            <SearchFilter v-model="filterBy" />
          </div>

          <div v-if="filteredRecoverings.length > 0" class="grid gap-3">
            <Accordion
              v-for="recovering in filteredRecoverings"
              :key="recovering.id"
              :title="recovering.entity.name"
              :subtitle="formatLegalNumber(recovering.entity.legalNumber)"
            >
              <template #header-right>
                <div class="flex-1 flex gap-2 justify-between items-center pl-8 pr-4">
                  <Btn
                    label="Novo Credor"
                    icon="i-carbon-add-filled"
                    outlined
                    disabled
                  />
                  <div class="font-bold flex no-wrap items-center gap-2">
                    Total: R$ 0
                    <Hint value="Total dos Cálculos Aprovados." />
                  </div>
                </div>
              </template>
              <div v-if="recovering.creditors.length > 0">
                <Accordion
                  v-for="creditor in recovering.creditors"
                  :key="creditor.id"
                  :title="recovering.entity.name"
                  :subtitle="formatLegalNumber(recovering.entity.legalNumber)"
                >
                  <template #header-right>
                    <div class="flex-1 flex items-center pl-8">
                      <Btn
                        label="Novo Credor"
                        icon="i-carbon-add-filled"
                        outlined
                        disabled
                      />
                    </div>
                  </template>
                  {{ recovering.creditors }}
                </Accordion>
              </div>
              <div v-else class="p-6 text-center">
                Nenhum Credor cadastrado para essa Recuperanda
              </div>
            </Accordion>
          </div>
          <div v-else class="text-lg text-center pt-5">
            Nenhuma Recuperanda nessa listagem...
          </div>
        </div>
      </div>
    </div>
    <Modal
      v-model="showTime"
      title="Participantes"
      hint="Esses são os Participantes e suas funções dentro do Projeto."
    >
      <div class="p-8 pt-4">
        <div
          v-for="(participants, key) in time"
          :key="key"
          class="mb-4"
        >
          <div class="font-bold mb-3">
            {{ key }}:
          </div>
          <div class="flex gap-2">
            <UserTag
              v-for="user in participants" :key="user.id"
              :model-value="user"
            />
          </div>
        </div>
      </div>
    </Modal>
  </div>
</template>

<route lang="yaml">
meta:
  authentication: true
</route>
