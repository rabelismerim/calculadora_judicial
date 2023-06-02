<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: boolean
  title?: string
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue', 'success'])

let loading = $ref(false)
const form = ref(null as any)
const stepper = ref(null as any)
const { step, hasError, setStep, nextStep, previousStep, clearErrors, validateAll, loadAll } = useSteps(1, 4, stepper, form)
const errorMessages = ref({})
const { setErrors, clearAll } = useBackendErrors(errorMessages)

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
  projectStart: null,
  projectEnd: null,
  dateRjRequest: null,
  dateRjFiling: null,
  dateCitation: null,
  legalManagerId: '',
  legalPartnerId: '',
  financialManagerId: '',
  financialPartnerId: '',
  calculationManagerId: '',
  executors: [],
  reviewers: [],
  approvers: [],
  specialApprovers: [],
  processNumber: '',
}
let newProject = $ref(clone(nullProject))
const clear = async () => {
  newProject = clone(nullProject)
  await delay(0.5)
  form.value.resetValidation()
  setStep(1)
  clearAll()
  clearErrors()
}
const addRecovering = () => {
  newProject.recoverings.push(clone(nullRecovering))
}
const removeRecovering = (index: number) => {
  newProject.recoverings.splice(index, 1)
}
const onSubmit = async () => {
  validateAll()
  if (hasError.value.includes(true)) {
    throwError({
      id: 'SUBMIT_ERROR',
      message: 'Você precisa resolver todos os problemas antes de concluir!',
    })
    return
  }
  try {
    loading = true
    const { id, description }: any = await projectService.newProject(newProject)
    if (id) {
      notify({ id, message: `Novo: ${description} criado com sucesso!` })
      emit('success')
    }
  }
  catch (error) {
    setErrors(error)
    await delay (0.01)
    validateAll()
    printError('ERROR ON CREATE NEWPROJECT:', error)
  }
  finally {
    loading = false
  }
}

// Options Helpers list
let users = $ref([])
const approvers = computed(() => users
  .filter(({ groups }: any) => {
    const groupNames = groups.map(({ name }: any) => name)
    return ['Gestor Jurídico', 'Gestor Cálculo', 'Gestor Financeiro']
      .some((group: string) => groupNames.includes(group))
  }))
const specialApprovers = computed(() => users
  .filter(({ groups }: any) => groups.map(({ name }: any) => name).includes('Sócio')))
let judges = $ref([])
const addJudge = async (description: string) => projectService.newJudge(description)
let lawyers = $ref([])
const addLawyer = async (description: string) => projectService.newLawyer(description)
let courts = $ref([])
const addCourt = async (description: string) => projectService.newCourt(description)
let regions = $ref([])
const addRegion = async (description: string) => projectService.newRegion(description)
onMounted(async () => {
  loadAll()
  loading = true
  try {
    users = await usersService.getUsers()
    judges = await projectService.getJudges()
    lawyers = await projectService.getLawyers()
    courts = await projectService.getCourts()
    regions = await projectService.getRegions()
  }
  catch (error) {
    printError('ERROR ON LOAD OPTIONS OF NEWPROJECT:', error)
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
              class="sm:col-span-2"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="description"
            />
            <InputTags
              v-model="newProject.engagements"
              label="Engagements"
              class="sm:col-span-2"
              :rules="[(value: any) => value.length > 0 || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="engagement.non_field_errors"
            />
            <InputText
              v-model="newProject.processNumber"
              label="Número de Processo"
              maxlength="25"
              mask="#######-##.####.#.##.####"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="process_number"
            />
            <InputDate
              v-model="newProject.dateRjRequest"
              label="Data de Pedido da Recuperação Judicial"
              :rules="[
                (value: any) => value.length === 0 || value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
              :error-messages="errorMessages"
              error-key="date_rj_request"
            />
            <InputDate
              v-model="newProject.dateRjFiling"
              label="Data de Ajuizamento da Recuperação Judicial"
              :rules="[
                (value: any) => value.length === 0 || value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
              :error-messages="errorMessages"
              error-key="date_rj_filling"
            />
            <InputDate
              v-model="newProject.dateCitation"
              label="Data da Citação"
              :rules="[
                (value: any) => value.length === 0 || value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
              :error-messages="errorMessages"
              error-key="date_citation"
            />
            <InputDate
              v-model="newProject.projectStart"
              label="Data de Início do Projeto"
              :rules="[
                (value: any) => !!value || 'É um campo obrigatório',
                (value: any) => value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value: any) => /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
              :error-messages="errorMessages"
              error-key="project_start"
            />
            <InputDate
              v-model="newProject.projectEnd"
              label="Data de Encerramento do Projeto"
              :rules="[
                (value: any) => value.length === 0 || value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
              :error-messages="errorMessages"
              error-key="project_end"
            />
            <InputSelect
              v-model="newProject.judgeId"
              v-model:options="judges"
              label="Juiz"
              :to-add="addJudge"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="judge_id"
            />
            <InputSelect
              v-model="newProject.lawyerId"
              v-model:options="lawyers"
              label="Advogado"
              :to-add="addLawyer"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="lawyer_id"
            />
            <InputSelect
              v-model="newProject.regionId"
              v-model:options="regions"
              label="Comarca"
              :to-add="addRegion"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="region_id"
            />
            <InputSelect
              v-model="newProject.courtId"
              v-model:options="courts"
              label="Vara"
              :to-add="addCourt"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="court_id"
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
            v-for="(recovering, index) in newProject.recoverings as any[]"
            :key="index"
            class="grid items-stretch grid-cols-[1fr_1fr_42px] gap-x-4"
            data-step="2"
          >
            <InputText
              v-model="recovering.name"
              label="Recuperanda"
              :rules="[(value: any) => !!value || 'Este Campo é obrigatório']"
              :error-messages="errorMessages"
              :error-key="`recoverings.${index}.entity.name`"
            />
            <InputLegal
              v-model="recovering.legalNumber"
              :rules="[(value: any) => !!value || 'Este Campo é obrigatório']"
              :error-messages="errorMessages"
              :error-key="`recoverings.${index}.entity.legal_number`"
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
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="financial_partner_id"
            />
            <InputUser
              v-model="newProject.legalPartnerId"
              label="Sócio Jurídico"
              :users="users"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="legal_partner_id"
            />
            <InputUser
              v-model="newProject.financialManagerId"
              label="Gerente Financeiro"
              :users="users"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="financial_manager_id"
            />
            <InputUser
              v-model="newProject.legalManagerId"
              label="Gerente Jurídico"
              :users="users"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="legal_manager_id"
            />
            <InputUser
              v-model="newProject.calculationManagerId"
              label="Gerente de Cálculo"
              :users="users"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="calculation_manager_id"
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
              :rules="[(value: any) => value.length > 0 || 'Este campo é obrigatório!']"
              :error-messages="errorMessages"
              error-key="executors"
            />
            <InputUsers
              v-model="newProject.reviewers"
              :users="users"
              label="Revisores"
              :rules="[(value: any) => value.length > 0 || 'Este campo é obrigatório!']"
              :error-messages="errorMessages"
              error-key="reviewers"
            />
            <InputUsers
              v-model="newProject.approvers"
              :users="approvers"
              label="Aprovadores"
              :rules="[(value: any) => value.length > 0 || 'Este campo é obrigatório!']"
              :error-messages="errorMessages"
              error-key="approvers"
            />
            <InputUsers
              v-model="newProject.specialApprovers"
              :users="specialApprovers"
              label="Aprovadores Especiais"
              :error-messages="errorMessages"
              error-key="special_approvers"
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
          type="button"
          @click="previousStep"
          @press="previousStep"
        />
        <Btn
          v-if="step < 4"
          label="Próximo"
          outlined
          type="button"
          @click="nextStep"
          @press="nextStep"
        />
        <Btn
          v-if="step === 4"
          label="Concluir"
          type="button"
          :loading="loading"
          loading-label="Criando Projeto..."
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
