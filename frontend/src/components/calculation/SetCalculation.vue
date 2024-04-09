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
  claims: [],
}
const calculationForm: any = ref(null as any)
let localCalculation: any = $ref(clone(nullCalculation))
watchEffect(() => {
  if (props.calculation?.id)
    localCalculation = clone(props.calculation)
})

const submit = async () => {
  if (!localCalculation.claims?.length) {
    throwError({ message: 'Você precisa adicionar no mínimo um pleito ao Cálculo!' })
    return
  }

  loading = true
  try {
    const { id } = await calculationService.setCalculation({ ...localCalculation, creditorId: props.creditorId })
    if (props.calculation?.id && id)
      notify({ message: `Cálculo ${localCalculation.id ? 'editado' : 'criado'} com sucesso!` })
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

let coins = $ref([])
let classes = $ref([])
const loadOptions = async () => {
  try {
    const result = await creditorsService.getOptions()
    coins = result.coinOptions
    classes = result.classesOptions
  }
  catch (error) {
    printError('ERROR ON LOAD COINS:', error)
  }
}

let selectedClaim = $ref(undefined as any)
let creditorClaims = $ref([] as any[])
watchEffect(async () => {
  if (props.creditorId) {
    const result = await creditorsService.getCreditorClaims(props.creditorId)
    creditorClaims = result.map((claim: any) => ({
      id: claim?.id,
      description: `${claim?.incident?.number} ⇒ ${claim?.coins?.coinDisplay} ${formatNumber(claim?.coins?.value, 2)} ⇒ ${claim?.classes?.classeDisplay}`,
      incidentId: claim?.incident?.id,
      classeId: claim?.classes?.classe,
      value: claim?.coins?.value,
      coin: claim?.coins?.coin,
      coinDisplay: claim?.coins?.coinDisplay,
    }))
  }
})
const filteredClaims = $computed(() => creditorClaims
  .filter(claim => localCalculation.coin === claim.coin && localCalculation.incidentId === claim.incidentId))
const addClaim = () => {
  if (!selectedClaim) {
    localCalculation.claims.push({
      value: 0,
      coin: localCalculation.coin,
      incidentId: localCalculation.incidentId,
    })
    return
  }
  if (!localCalculation.claims.map(({ id }: any) => id).includes(selectedClaim?.id))
    localCalculation.claims.push(selectedClaim)
  selectedClaim = undefined
}
const removeClaim = (index: number) => {
  if (index === undefined)
    return
  localCalculation.claims.splice(index, 1)
}

onMounted(() => {
  loadRates()
  loadOptions()
  loadIncidents()
})
</script>

<template>
  <Modal
    :loading="loading"
    :model-value="open"
    :title="`${localCalculation.id ? 'Edição do' : 'Criar um novo'} Cálculo`"
    hint="Para criar um cálculo é preciso escolher um incidente."
    modal-class="max-w-200"
    @close="close"
  >
    <QForm
      ref="calculationForm"
      @submit="submit"
    >
      <div class="pt-2 px-4 grid grid-cols-6 gap-x-4 max-h-70vh overflow-y-auto">
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
        <QSelect
          v-model="localCalculation.coin"
          :options="coins"
          label="Moeda"
          outlined
          emit-value
          map-options
          option-value="id"
          option-label="legend"
          :disable="loading"
          :rules="[(value: string) => !!value || 'Este Campo é obrigatório!']"
          dense
          class="col-span-2"
        />
        <InputSelect
          v-model="localCalculation.incidentId"
          v-model:options="incidents"
          label="Número de Incidente"
          :to-add="addIncident"
          :rules="[(value: any) => !!value || 'É um campo obrigatório']"
          :disabled="loading || !!localCalculation.id"
          class="col-span-4"
        />
        <div class="col-span-6 bg--primary/12 border-black/12 border-1 rounded mb-5 gap-4">
          <div class="col-span-4 flex flex-1 gap-4 border-b-1 border-black/12 p-2">
            <InputSelect
              v-model="selectedClaim"
              v-model:options="filteredClaims"
              label="Pleitos do Credor"
              :disabled="loading"
              :empty-message="localCalculation.coin && localCalculation.incidentId ? 'Nenhum Pleito encontrado...' : 'Selecione Moeda e Incidente!'"
              class="flex-1"
              :emit-value="false"
            />
            <button
              type="button" class="bg--base px-4 text--primary border--primary border-1 font-bold hover:bg--primary/50 hover:text-white rounded h-10 flex justify-center items-center"
              :disabled="!localCalculation.coin || !localCalculation.incidentId"
              @click="addClaim"
            >
              {{ selectedClaim ? 'Adicionar' : 'Criar' }} Pleito
              <QTooltip v-if="localCalculation.coin && localCalculation.incidentId">
                Clique para adicionar um Pleito
              </QTooltip>
              <QTooltip v-else>
                Selecione Moeda e Incidente!
              </QTooltip>
            </button>
          </div>
          <div v-if="localCalculation.claims?.length" class="p-2">
            <div
              v-for="(claim, index) in localCalculation.claims"
              :key="index"
              class="grid grid-cols-[1fr_1fr_40px] gap-2"
              :class="{ 'mt-2': index !== 0 }"
            >
              <QInput
                v-model="claim.value"
                type="number"
                label="Valor"
                :disable="!!claim.id"
                outlined
                dense
              />
              <QSelect
                v-model="claim.classeId" label="Classe"
                :disable="!!claim.id"
                :options="classes"
                option-label="legend"
                option-value="id"
                emit-value
                map-options
                outlined
                dense
              />
              <div
                class="border-1 border--error rounded text--error p-2 hover:bg--error/20 cursor-pointer tween flex justify-center items-center text-xl"
                @click="removeClaim(index)"
              >
                <div class="i-carbon-trash-can" />
              </div>
            </div>
          </div>
          <div v-else class="text-center text--primary p-2">
            Adicione um Pleito...
          </div>
        </div>
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
          class="col-span-3"
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
          class="col-span-3"
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
