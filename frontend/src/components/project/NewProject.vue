<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: boolean
  title?: string
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue'])

let loading = $ref(false)
const form = ref(null) as any
const stepper = ref(null) as any
const { step, hasError, setStep, nextStep, previousStep, clearErrors, validateAll } = useSteps(1, stepper, form)

// Project related
const nullRecovering = {
  name: '',
  legalNumber: '',
}
const nullProject = {
  judgeId: '',
  lawyerId: '',
  regionId: '',
  courtId: '',
  engagements: [],
  recoverings: [clone(nullRecovering)],
  description: '',
  start: null,
  end: null,
  status: '',
  legalManagerId: '',
  legalPartnerId: '',
  financialManagerId: '',
  financialPartnerId: '',
  calculationManagerId: '',
  executors: [],
  approvers: [],
  reviewers: [],
  processNumber: '',
}
let newProject = $ref(clone(nullProject))
const clear = async () => {
  newProject = clone(nullProject)
  await delay(0.5)
  form.value.resetValidation ()
  setStep(1)
  clearErrors()
}
const addRecovering = () => {
  newProject.recoverings.push(clone(nullRecovering))
}
const removeRecovering = (index: number) => {
  newProject.recoverings.splice(index, 1)
}
const onSubmit = async () => {
  validateAll(4)
  if (hasError.value.includes(true)) {
    throwError({
      id: 'SUBMIT_ERROR',
      message: 'Você precisa preencher os campos obrigatórios!',
    })
    return
  }
  try {
    loading = true
    const result = await projectService.newProject(newProject)
    console.warn('NEW PROJECT', { result })
  }
  catch (error) {
    throwError(error)
  }
  finally {
    loading = false
  }
}

// Options Helpers list
let users = $ref([])
let judges = $ref([])
const addJudge = async (description: string) => projectService.newJudge(description)
let courts = $ref([])
const addCourt = async (description: string) => projectService.newCourt(description)
let regions = $ref([])
const addRegion = async (description: string) => projectService.newRegion(description)
onMounted(async () => {
  loading = true
  try {
    users = await usersService.getUsers()
    judges = await projectService.getJudges()
    courts = await projectService.getCourts()
    regions = await projectService.getRegions()
  }
  catch (error) {
    throwError(error)
  }
  finally {
    loading = false
  }
})
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Cadastro de Projeto"
    hint="Existe um cadastro prévio para o cadastro de projetos na ferramenta."
    :loading="loading"
    @update:model-value="(value: boolean) => emit('update:modelValue', value)"
    @close="clear"
  >
    <QForm ref="form" @submit.prevent="onSubmit">
      <QStepper
        ref="stepper"
        v-model="step"
        color="primary"
        animated
        header-nav
        keep-alive
        flat
        header-class="shadow-md"
      >
        <QStep
          :name="1"
          title="Informações Principais"
          icon="o_description"
          :error="hasError.at(1)"
          class="overflow-y-auto max-h-[calc(100vh-326px)]"
        >
          <div data-step="1" class="grid sm:grid-cols-2 gap-x-4">
            <InputText
              v-model="newProject.description"
              label="Nome do Projeto"
              :rules="[value => !!value || 'É um campo obrigatório']"
              class="sm:col-span-2"
            />
            <InputTags
              v-model="newProject.engagements"
              label="Engagements"
              class="sm:col-span-2 mb-5"
            />
            <InputText
              v-model="newProject.processNumber"
              label="Número de Processo"
              maxlength="15"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
            <InputDate
              v-model="newProject.start"
              label="Data do Pedido de Recuperação Judicial"
              :rules="[
                value => !!value || 'É um campo obrigatório',
                (value) => value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value) => /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
            />
            <InputSelect
              v-model="newProject.judgeId"
              v-model:options="judges"
              label="Juiz"
              :to-add="addJudge"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
            <InputSelect
              v-model="newProject.lawyerId"
              v-model:options="judges"
              label="Advogado"
              :to-add="addJudge"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
            <InputSelect
              v-model="newProject.regionId"
              v-model:options="regions"
              label="Comarca"
              :to-add="addRegion"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
            <InputSelect
              v-model="newProject.courtId"
              v-model:options="courts"
              label="Vara"
              :to-add="addCourt"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
          </div>
        </QStep>

        <QStep
          :name="2"
          title="Recuperandas"
          icon="o_store"
          :error="hasError.at(2)"
          class="relative overflow-y-auto max-h-[calc(100vh-326px)] min-h-87 overflow-x-hidden"
        >
          <div
            v-for="(recovering, index) in newProject.recoverings"
            :key="index"
            class="grid items-stretch sm:grid-cols-[1fr_1fr_42px] gap-x-4"
            data-step="2"
          >
            <InputText
              v-model="recovering.name"
              label="Recuperanda"
              :rules="[value => !!value || 'Este Campo é obrigatório']"
            />
            <InputLegal
              v-model="recovering.legalNumber"
            />
            <div
              class="border-1 border--error hover:border-black/22 rounded color--error hover:bg--error hover:color-white flex justify-center items-center text-lg cursor-pointer mb-5"
              tabindex="0"
              @click="removeRecovering(index)"
              @keyup.space="removeRecovering(index)"
            >
              <div class="i-carbon-trash-can" />
            </div>
          </div>
          <div class="sticky bg--base p-2 bottom-0 flex justify-center">
            <Btn
              label="Adicionar Nova Recuperanda"
              icon="i-carbon-add-filled"
              outlined
              @click="addRecovering"
            />
          </div>
        </QStep>

        <QStep
          :name="3"
          title="Responsáveis"
          icon="o_assignment_ind"
          :error="hasError.at(3)"
          class="overflow-y-auto min-h-87  max-h-[calc(100vh-326px)]"
        >
          <div data-step="3" class="grid sm:grid-cols-2 gap-x-4">
            <InputUser
              v-model="newProject.financialPartnerId"
              label="Sócio Financeiro"
              :users="users"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
            <InputUser
              v-model="newProject.legalPartnerId"
              label="Sócio Jurídico"
              :users="users"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
            <InputUser
              v-model="newProject.financialManagerId"
              label="Gerente Financeiro"
              :users="users"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
            <InputUser
              v-model="newProject.legalManagerId"
              label="Gerente Jurídico"
              :users="users"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
            <InputUser
              v-model="newProject.calculationManagerId"
              label="Gerente de Cálculo"
              :users="users"
              :rules="[value => !!value || 'É um campo obrigatório']"
            />
          </div>
        </QStep>

        <QStep
          :name="4"
          title="Times e Papéis"
          icon="o_people"
          :error="hasError.at(4)"
          class="relative overflow-y-auto max-h-[calc(100vh-326px)] min-h-87 pb-0 pt-6 px-6 overflow-x-hidden"
        >
          <div
            class=""
            data-step="4"
          >
            <InputUsers
              v-model="newProject.executors"
              :users="users"
              label="Executores"
              :rules="[value => value.length > 0 || 'Este campo é obrigatório!']"
            />
            <InputUsers
              v-model="newProject.approvers"
              :users="users"
              label="Aprovadores"
              :rules="[value => value.length > 0 || 'Este campo é obrigatório!']"
            />
            <InputUsers
              v-model="newProject.reviewers"
              :users="users"
              label="Revisores"
              :rules="[value => value.length > 0 || 'Este campo é obrigatório!']"
            />
          </div>
        </QStep>
      </QStepper>

      <div class="relative flex justify-end gap-2 p-3 border-t-1 ">
        <QLinearProgress
          v-if="loading"
          indeterminate
          color="secondary"
          class="absolute top-0 left-0"
          size="xs"
        />
        <Btn
          v-if="step > 1"
          label="Anterior"
          outlined
          tag="div"
          @click="previousStep"
          @press="previousStep"
        />
        <Btn
          v-if="step < 4"
          label="Próximo"
          outlined
          tag="div"
          @click="nextStep"
          @press="nextStep"
        />
        <Btn
          v-if="step === 4"
          label="Concluir"
          tag="div"
          :loading="loading"
          loading-label="Criando Projeto..."
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
