<script setup lang="ts">
const attrs = useAttrs() as any

let loading = $ref(false)
const filterBy = $ref('')
const showParticipants = $ref(false)
const tab = $ref('all')
let project: any = $ref({})

const filteredRecoverings = computed(() => {
  if (tab === 'all')
    return project?.recoverings || []
  return project?.recoverings?.filter(() => false)
})

const participants = computed(() => {
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
  <Page
    menu-label="Informações Principais"
    :loading="loading"
    :links="[{ label: 'Projetos', url: '/projetos' }, { label: project.description }]"
  >
    <template #menu>
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
    </template>

    <Header :title="`Projeto ${project.description}`">
      <Btn
        label="Participantes"
        icon="i-carbon-events"
        outlined
        @click="showParticipants = true"
      />
      <Btn
        label="Editar"
        icon="i-carbon-edit"
        disabled
      />
    </Header>

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

    <Header title="Cálculos">
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Cálculos"
          @click="loadProject"
        />
      </template>
      <Btn
        label="Exportar Cálculos Válidos"
        icon="i-carbon-document-export"
        disabled
      />
    </Header>

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

    <template #out>
      <Modal
        v-model="showParticipants"
        title="Participantes"
        hint="Esses são os Participantes e suas funções dentro do Projeto."
      >
        <div class="p-8 pt-4">
          <div
            v-for="(group, key) in participants"
            :key="key"
            class="mb-4"
          >
            <div class="font-bold mb-3">
              {{ key }}:
            </div>
            <div class="flex gap-2">
              <UserTag
                v-for="user in group" :key="user.id"
                :model-value="user"
              />
            </div>
          </div>
        </div>
      </Modal>
    </template>
  </Page>
</template>

<route lang="yaml">
meta:
  authentication: true
</route>
