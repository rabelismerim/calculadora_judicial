<script setup lang="ts">
const props = withDefaults(defineProps<{
  open: boolean
  options: any
  calculation?: any
  creditorId?: string
  projectId?: string
}>(), {

})
const emit = defineEmits(['update:open', 'update:calculation', 'success'])

let loading = $ref(false)

const nullCalculation = {
  isAdm: true,
  appealCredit: false,
  appealDeposit: false,
  hasAdvocativeHours: false,
}
const calculationForm: any = ref(null as any)
let localCalculation: any = $ref(clone(nullCalculation))
watchEffect(() => {
  if (props.calculation?.id)
    localCalculation = clone(props.calculation)
})

const submit = async () => {
  loading = true
  try {
    const { id } = await calculationService.setCalculation({ ...localCalculation, creditorId: props.creditorId })
    if (props.calculation?.id && id)
      notify({ message: 'Cálculo editado com sucesso!' })
    emit('success', id)
    emit('update:open', false)
  }
  catch (error) {
    printError('ERROR ON SET CALCULATION:', error)
  }
  finally {
    loading = false
  }
}
const close = () => {
  emit('update:open', false)
  calculationForm.value.reset()
  localCalculation = clone(props.calculation ? props.calculation : nullCalculation)
}

let rates = $ref([] as any[])
const loadRates = async () => {
  rates = await ratesService.getRates()
}

let incidents: any[] = $ref([])
const addIncident = async (incidentNumber: string) => {
  loading = true
  try {
    const result: any = await calculationService.newIncident(incidentNumber)
    const { id, number } = result
    return { id, number, description: number }
  }
  catch (error) {
    printError('ERROR ON LOAD INCIDENSTS:', error)
  }
  finally {
    loading = false
  }
}
const loadIncidents = async () => {
  try {
    incidents = await calculationService.getIncidents()
  }
  catch (error) {
    printError('ERROR ON LOAD INCIDENSTS:', error)
  }
}

onMounted(() => {
  loadRates()
  loadIncidents()
})
</script>

<template>
  <Modal
    :loading="loading"
    :model-value="open"
    :title="`${localCalculation.id ? 'Editar' : 'Criar'} um Novo Cálculo`"
    hint="Para criar um cálculo é preciso escolher um incidente."
    modal-class="max-w-200"
    @close="close"
  >
    <QForm
      ref="calculationForm"
      @submit="submit"
    >
      <div class="px-4 pt-4 grid grid-cols-6 gap-x-4">
        <InputSelect
          v-model="localCalculation.incidentId"
          v-model:options="incidents"
          label="Número de Incidente"
          :to-add="addIncident"
          :rules="[(value: any) => !!value || 'É um campo obrigatório']"
          :disabled="loading || !!localCalculation.id"
          class="col-span-4"
        />
        <QSelect
          v-model="localCalculation.rateId"
          :options="rates"
          label="Taxa"
          outlined
          emit-value
          map-options
          option-value="id"
          option-label="index"
          :disable="loading"
          :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
          dense
          class="col-span-2"
        />
        <QSelect
          v-model="localCalculation.occurrence"
          :options="options.ocurrences"
          label="Ocorrência"
          outlined
          emit-value
          map-options
          option-value="id"
          option-label="legend"
          :disable="loading"
          :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
          dense
          :class="['CA'.includes(localCalculation.occurrence) ? 'col-span-3' : 'col-span-6']"
        />
        <InputDate
          v-if="localCalculation.occurrence === 'C'"
          v-model="localCalculation.dateCitation"
          label="Data da Citação"
          :rules="[
            (value: any) => !!value || 'Campo é obrigatório!',
            (value: any) => value.length === 0 || value.length === 10 || 'Padrão ##/##/####',
            (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Data inválida!',
          ]"
          class="col-span-3"
        />
        <InputDate
          v-if="localCalculation.occurrence === 'A'"
          v-model="localCalculation.dateRjFiling"
          label="Data de Ajuizamento"
          :rules="[
            (value: any) => !!value || 'Campo é obrigatório!',
            (value: any) => value.length === 0 || value.length === 10 || 'Padrão ##/##/####',
            (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Data inválida!',
          ]"
          class="col-span-3"
        />
        <InputDate
          v-if="localCalculation.occurrence && !'CA'.includes(localCalculation.occurrence)"
          v-model="localCalculation.dateCitation"
          label="Data da Citação"
          :rules="[
            (value: any) => value.length === 0 || value.length === 10 || 'Padrão ##/##/####',
            (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Data inválida!',
          ]"
          class="col-span-3"
        />
        <InputDate
          v-if="localCalculation.occurrence && !'CA'.includes(localCalculation.occurrence)"
          v-model="localCalculation.dateRjFiling"
          label="Data de Ajuizamento"
          :rules="[
            (value: any) => value.length === 0 || value.length === 10 || 'Padrão ##/##/####',
            (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Data inválida!',
          ]"
          class="col-span-3"
        />
        <InputDate
          v-model="localCalculation.dateCreditAuth"
          label="Data da Certidão de Habilitação de Crédito"
          :rules="[
            (value: any) => value.length === 0 || value.length === 10 || 'Padrão ##/##/####',
            (value: any) => value.length === 0 || /^[0-3]\d\/[0-1]\d\/[\d]+$/.test(value) || 'Data inválida!',
          ]"
          class="col-span-3"
          @update:model-value="(value: any) => {
            if (!value) localCalculation.numPagFlsCreditAuthDate = undefined
          }"
        />
        <QInput
          v-model="localCalculation.numPagFlsCreditAuthDate"
          type="number"
          label="Número da Página da Certidão de Habilitação de Crédito"
          :disable="!localCalculation.dateCreditAuth"
          outlined
          dense
          class="col-span-3 mb-5"
        />
        <InputToggle
          v-model="localCalculation.appealDeposit"
          label="N7 - Houve levantamento de depósito concursal"
          class="col-span-3 mb-5"
          @update:model-value="(value: any) => {
            if (!value) localCalculation.numPagFlsAppealDeposit = undefined
          }"
        />
        <QInput
          v-model="localCalculation.numPagFlsAppealDeposit"
          type="number"
          label="Número da Página do depósito Recursal"
          :disable="!localCalculation.appealDeposit"
          outlined
          dense
          class="col-span-3 mb-5"
        />
        <InputNumber
          v-model="localCalculation.recurralDeposit"
          label="Depósito Recursal Liberado"
          class="col-span-3"
        />
        <InputToggle
          v-model="localCalculation.hasAdvocativeHours"
          label="Horários advocatícios"
          class="col-span-3 mb-5"
        />
        <label class="flex gap-4 md:gap-12 items-center mb-4 col-span-6">
          <div class="font-bold color-gray-8 text-md">Fase do Cálculo</div>
          <BtnToggle
            v-model="localCalculation.isAdm"
            :disabled="!!localCalculation.id"
            class="bg--base flex-1"
            :items="[
              { label: 'Administrativa', value: true },
              { label: 'Judiciária', value: false },
            ]"
          />
        </label>
      </div>
      <div class="flex justify-end p4 border-t-1 border-black/12">
        <Btn
          :label="`${localCalculation.id ? 'Editar' : 'Criar'} Cálculo`"
          type="submit"
          :loading-label="`${localCalculation.id ? 'Editando' : 'Criando'} novo Cálculo...`"
          :loading="loading"
        />
      </div>
    </QForm>
  </Modal>
</template>
