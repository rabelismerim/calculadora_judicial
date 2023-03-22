<script setup lang="ts">
const attrs = useAttrs() as any
const router = useRouter()

let loading = $ref(false)
const filterBy = $ref('')
const sideOpen = $ref(true)
const showTime = $ref(false)
let project: any = $ref({})
let users: any = $ref([])

const time = computed(() => {
  const { users: usersList = [] } = project
  return usersList.reduce((acc: any, current: any) => {
    const { id, username, groups } = current
    groups.forEach(({ name }: any) => {
      if (!acc[name])
        acc[name] = []
      const user = users.find((user: any) => id === user.id)
      if (user)
        acc[name].push(user)
    })
    return acc
  }, {})
})

onMounted(async () => {
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
      class="relative flex-1 grid grid-cols-[320px_1fr] tween-800"
      :class="{ '-translate-x-284px w-[calc(100vw+284px)]': !sideOpen }"
    >
      <div class="relative bg--base pb-0 pr-9">
        <div class="h-full max-h-[calc(100vh-96px)] overflow-x-hidden overflow-y-auto scroll-left">
          <div class="p-8 pr-0">
            <h2 class="font-bold text-2xl bg--base sticky top-0 py-4">
              Informações Principais
            </h2>
            <div>
              <ProjectDetailCell label="Engagment">
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
                {{ toProperName(project?.judge?.description || '-') }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Comarca">
                {{ project?.region?.description || '-' }}
              </ProjectDetailCell>

              <ProjectDetailCell label="Vara">
                {{ project?.court?.description || '-' }}
              </ProjectDetailCell>
            </div>
          </div>
        </div>
        <div
          class="absolute right-0 top-0 bottom-0 p-1 flex flex-col items-center gap-4 hover:bg--secondary/10 cursor-pointer pt-10 tween"
          @click="sideOpen = !sideOpen"
        >
          <div class="i-carbon-chevron-right text-lg tween-800" :class="{ 'rotate-180': sideOpen }" />
          <div class="text-vertical whitespace-nowrap font-bold text-lg tween-800" :class="{ 'opacity-0': sideOpen }">
            Informações Principais
          </div>
        </div>
      </div>

      <div class="px-8 py-8 max-h-[calc(100vh-96px)] overflow-y-auto overflow-x-hidden flex justify-center">
        <div class="max-w-[min(1600px,100%)]">
          <button
            class="mb-8 group flex gap-1 items-center uppercase font-semibold hover:text--secondary tween-800 z-1"
            @click="router.push({ path: '/projetos' })"
          >
            <div class="i-carbon-chevron-left group-hover:-translate-x-1 tween-800" />
            Voltar
          </button>

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
                outlined
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
            <GraphLine
              :values="[]"
              title="Quantidade de Cálculos por Classe"
              hint="Classes na Recuperação Judicial:\n  • Classe I - Créditos Trabalhistas\n  • Classe II - Créditos com Garantia Real\n  • Classe III - Créditos Quirográficos\n  • Classe IV - Créditos enquadrados como Microempresa ou Empresa de pequeno porte."
            />
            <GraphLine
              :values="[]"
              title="Valores dos Cálculos por Classe (mil R$)"
              hint="Classes na Recuperação Judicial:\n  • Classe I - Créditos Trabalhistas\n  • Classe II - Créditos com Garantia Real\n  • Classe III - Créditos Quirográficos\n  • Classe IV - Créditos enquadrados como Microempresa ou Empresa de pequeno porte."
            />
          </div>

          <div class="mb-8 flex justify-between gap-4">
            <h1 class="font-bold text-4xl">
              Cálculos
            </h1>
            <div class="flex gap-2">
              <Btn
                label="Exportar Cálculos Válidos"
                icon="i-carbon-document-export"
                disabled
              />
            </div>
          </div>

          <div v-if="project?.recoverings" class="grid gap-3">
            <Accordion
              v-for="recovering in project?.recoverings"
              :key="recovering.id"
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
          <div v-else class="text-lg">
            Nenhuma Recuperanda Cadastrada no momento...
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
            {{ key }}es:
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
