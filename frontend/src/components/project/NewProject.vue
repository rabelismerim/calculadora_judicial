<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: boolean
  title?: string
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue'])

const tabs = [
  {
    name: 'main',
    label: 'Informações Principais',
  },
  {
    name: 'recovering',
    label: 'Recuperandas',
  },
  {
    name: 'team',
    label: 'Time e Papéis',
  },
]
const { currentTab, isFirstTab, isLastTab, nextTab, lastTab } = useTabs('main', tabs)

const newProject = $ref({
  judgeId: '',
  lawyerId: '',
  regionId: '',
  courtId: '',
  engagements: [],
  recoverings: [],
  description: '',
  start: null,
  end: null,
  status: '',
  managerId: undefined,
  partnerId: '',
  users: [],
  processNumber: '',
})

let recoverings = $ref([])
let users = $ref([])
onMounted(async () => {
  try {
    users = await usersService.getUsers()
    recoverings = await recoveringService.getRecoverings()
  }
  catch (error) {
    throwError(error)
  }
})
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Cadastro de Projeto"
    hint="Existe um cadastro prévio para o cadastro de projetos na ferramenta."
    @update:model-value="(value: boolean) => emit('update:modelValue', value)"
  >
    <QForm @submit.prevent>
      <QTabs
        v-model="currentTab"
        dense
        class="text-grey"
        active-color="secondary"
        align="left"
        narrow-indicator
        no-caps
      >
        <QTab
          v-for="{ name, label } in tabs"
          :key="name"
          :name="name"
          :label="label"
        />
      </QTabs>

      <QSeparator />

      <QTabPanels v-model="currentTab" animated>
        <QTabPanel name="main">
          <div class="grid sm:grid-cols-2 gap-4 p-2">
            <InputTags
              v-model="newProject.engagements"
              label="Engagements *"
              class="sm:col-span-2"
            />
            <InputUser
              v-model="newProject.managerId"
              label="Sócio Financeiro"
              :users="users"
            />
            <InputUser
              v-model="newProject.managerId"
              label="Sócio Jurídico"
              :users="users"
            />
            <InputUser
              v-model="newProject.managerId"
              label="Gerente Financeiro"
              :users="users"
            />
            <InputUser
              v-model="newProject.managerId"
              label="Gerente Jurídico"
              :users="users"
            />
            <InputUser
              v-model="newProject.managerId"
              label="Gerente de Cálculo"
              :users="users"
            />
            <InputDate
              v-model="newProject.start"
              label="Data do Pedido de Recuperação Judicial"
            />
            <InputSelect
              v-model="newProject.judgeId"
              label="Juiz"
              :props="[]"
            />
            <InputText
              v-model="newProject.processNumber"
              label="Número de Processo"
            />
          </div>
        </QTabPanel>

        <QTabPanel name="recovering">
          <div class="text-h6">
            Alarms
          </div>
          Lorem ipsum dolor sit amet consectetur adipisicing elit.
        </QTabPanel>

        <QTabPanel name="team">
          <div class="text-h6">
            Movies
          </div>
          Lorem ipsum dolor sit amet consectetur adipisicing elit.
        </QTabPanel>
      </QTabPanels>
      <div class="flex justify-end gap-2 p-3 border-t-1 ">
        <Btn
          :disabled="isFirstTab"
          label="Anterior"
          outlined
          @click="lastTab"
        />
        <Btn
          :disabled="isLastTab"
          label="Próximo"
          outlined
          @click="nextTab"
        />
        <Btn
          label="Concluir"
          type="submit"
        />
      </div>
    </QForm>
  </Modal>
</template>
