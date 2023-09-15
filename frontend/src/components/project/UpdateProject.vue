<script setup lang="ts">
const props = withDefaults(defineProps<{
  modelValue: boolean
  project: any
  title?: string
  options: any
}>(), {
})
const emit = defineEmits(['update:modelValue', 'update:project', 'update:options', 'success'])

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
let editingProject = $ref({} as any)
watchEffect(() => {
  if (props.modelValue === true) {
    const newProject = clone(props.project)
    const { judge, lawyer, region, court, legalPartner, legalManager, financialPartner, financialManager, calculationManager } = newProject
    editingProject = {
      ...newProject,
      judgeId: judge?.id,
      lawyerId: lawyer?.id,
      regionId: region?.id,
      courtId: court?.id,
      legalPartnerId: legalPartner?.id,
      legalManagerId: legalManager?.id,
      financialPartnerId: financialPartner?.id,
      financialManagerId: financialManager?.id,
      calculationManagerId: calculationManager?.id,
    }
  }
})

const clear = async () => {
  editingProject = clone({})
  await delay(0.5)
  form.value.resetValidation()
  setStep(1)
  clearAll()
  clearErrors()
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
    const { id, description }: any = await projectService.updateProject(editingProject)
    if (id) {
      notify({ id, message: `Novo: ${description} atualizado com sucesso!` })
      emit('success')
      emit('update:modelValue', false)
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
const managers = computed(() => props.options?.users
  .filter(({ groups }: any) => {
    const groupNames = groups.map(({ name }: any) => name)
    return ['Gestor Jurídico', 'Gestor Cálculo', 'Gestor Financeiro']
      .some((group: string) => groupNames.includes(group))
  }))
const partners = computed(() => props.options?.users
  .filter(({ groups }: any) => {
    const groupNames = groups.map(({ name }: any) => name)
    return ['Sócio']
      .some((group: string) => groupNames.includes(group))
  }))
const specialApprovers = computed(() => props.options?.users
  .filter(({ groups }: any) => {
    const groupNames = groups.map(({ name }: any) => name)
    return ['Gestor Jurídico', 'Gestor Cálculo', 'Gestor Financeiro', 'Sócio']
      .some((group: string) => groupNames.includes(group))
  }))

const addJudge = async (description: string) => await projectService.newJudge(description)
const addLawyer = async (description: string) => await projectService.newLawyer(description)
const addCourt = async (description: string) => await projectService.newCourt(description)
const addRegion = async (description: string) => await projectService.newRegion(description)
const updateOption = (key: string, value: any) => {
  const newOptions = clone(props.options)
  newOptions[key] = value
  emit('update:options', newOptions)
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="`Edição do Projeto ${project.description}`"
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
        class="small"
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
              v-model="editingProject.description"
              label="Nome do Projeto"
              class="sm:col-span-2"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="description"
            />
            <InputTags
              v-if="editingProject.engagements"
              v-model="editingProject.engagements"
              label="Engagements"
              class="sm:col-span-2"
              :rules="[(value: any) => value.length > 0 || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="engagement.non_field_errors"
            />
            <InputText
              v-model="editingProject.processNumber"
              label="Número de Processo"
              maxlength="25"
              mask="#######-##.####.#.##.####"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="process_number"
            />
            <InputDate
              v-model="editingProject.dateRjRequest"
              label="Data de Pedido da Recuperação Judicial"
              :rules="[
                (value: any) => value.length === 0 || value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
              :error-messages="errorMessages"
              error-key="date_rj_request"
            />
            <InputDate
              v-model="editingProject.dateRjFiling"
              label="Data de Ajuizamento da Recuperação Judicial"
              :rules="[
                (value: any) => value.length === 0 || value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
              :error-messages="errorMessages"
              error-key="date_rj_filling"
            />
            <InputDate
              v-model="editingProject.projectStart"
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
              v-model="editingProject.projectEnd"
              label="Data de Encerramento do Projeto"
              :rules="[
                (value: any) => value.length === 0 || value.length === 10 || 'Precisa preencher o padrão ##/##/####',
                (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Precisa ser uma data válida!',
              ]"
              :error-messages="errorMessages"
              error-key="project_end"
            />
            <InputSelect
              v-model="editingProject.judgeId"
              :options="options.judges"
              label="Juiz"
              :to-add="addJudge"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="judge_id"
              @update:options="(value: any) => updateOption('judges', value)"
            />
            <InputSelect
              v-model="editingProject.lawyerId"
              :options="options.lawyers"
              label="Advogado"
              :to-add="addLawyer"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="lawyer_id"
              @update:options="(value: any) => updateOption('lawyers', value)"
            />
            <InputSelect
              v-model="editingProject.regionId"
              :options="options.regions"
              label="Comarca"
              :to-add="addRegion"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="region_id"
              @update:options="(value: any) => updateOption('regions', value)"
            />
            <InputSelect
              v-model="editingProject.courtId"
              :options="options.courts"
              label="Vara"
              :to-add="addCourt"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="court_id"
              @update:options="(value: any) => updateOption('courts', value)"
            />
          </div>
        </QStep>

        <QStep
          :name="2"
          title="Responsáveis"
          icon="o_assignment_ind"
          :error="hasError.at(2)"
          class="overflow-y-auto min-h-87  max-h-[calc(100vh-326px)]"
        >
          <div data-step="2" class="grid sm:grid-cols-2 gap-x-4">
            <InputUser
              v-model="editingProject.financialPartnerId"
              label="Sócio Financeiro"
              :users="partners"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="financial_partner_id"
            />
            <InputUser
              v-model="editingProject.legalPartnerId"
              label="Sócio Jurídico"
              :users="partners"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="legal_partner_id"
            />
            <InputUser
              v-model="editingProject.financialManagerId"
              label="Gerente Financeiro"
              :users="managers"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="financial_manager_id"
            />
            <InputUser
              v-model="editingProject.legalManagerId"
              label="Gerente Jurídico"
              :users="managers"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="legal_manager_id"
            />
            <InputUser
              v-model="editingProject.calculationManagerId"
              label="Gerente de Cálculo"
              :users="managers"
              :rules="[(value: any) => !!value || 'É um campo obrigatório']"
              :error-messages="errorMessages"
              error-key="calculation_manager_id"
            />
          </div>
        </QStep>

        <QStep
          :name="3"
          title="Times e Papéis"
          icon="o_people"
          :error="hasError.at(3)"
          class="relative overflow-y-auto max-h-[calc(100vh-326px)] min-h-87 pb-0 md:pt-6 md:px-6 overflow-x-hidden"
        >
          <div
            class=""
            data-step="3"
          >
            <InputUsers
              v-model="editingProject.executors"
              :users="options.users"
              label="Executores"
              :rules="[(value: any) => value?.length > 0 || 'Este campo é obrigatório!']"
              :error-messages="errorMessages"
              error-key="executors"
            />
            <InputUsers
              v-model="editingProject.reviewers"
              :users="options.users"
              label="Revisores"
              :rules="[(value: any) => value?.length > 0 || 'Este campo é obrigatório!']"
              :error-messages="errorMessages"
              error-key="reviewers"
            />
            <InputUsers
              v-model="editingProject.approvers"
              :users="managers"
              label="Aprovadores"
              :rules="[(value: any) => value?.length > 0 || 'Este campo é obrigatório!']"
              :error-messages="errorMessages"
              error-key="approvers"
            />
            <InputUsers
              v-model="editingProject.specialApprovers"
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
          v-if="step < 3"
          label="Próximo"
          outlined
          type="button"
          @click="nextStep"
          @press="nextStep"
        />
        <Btn
          v-if="step === 3"
          label="Concluir"
          type="button"
          :loading="loading"
          loading-label="Atualizando Projeto..."
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
