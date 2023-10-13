<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: any
  options: any
  title: string
  name: number
  creditorId: string
}>(), {
})
const emit = defineEmits(['update:model-value', 'save'])

let isLoading = $ref(false)
let isEditing = $ref(false)

const newCredit = {
  incidentId: null,
  classes: {
    classe: '1',
  },
  coins: {
    coin: 'B',
    value: 0,
  },
}
let localData = $ref([clone(newCredit)] as any[])
const data = computed({
  get() {
    return localData
  },
  set(newValue) {
    localData = newValue
  },
})
watchEffect(() => data.value = clone(props.modelValue))
const addNewCredit = () => {
  if (!isEditing)
    return
  data.value.push(clone(newCredit))
}
const removeCredit = (id: number | boolean) => {
  if (!isEditing || !id)
    return
  data.value.splice(id as number, 1)
}
const onSubmit = async () => {
  isLoading = true
  try {
    for (const item of data.value) {
      const payload = { ...item, creditorId: props.creditorId }
      await creditorsService.setCreditorClaim(payload)
    }
    isEditing = false
    emit('save')
  }
  catch (error) {
    printError('ERROR ON SUBMIT CREDITOR CLAIM:', error)
  }
  finally {
    isLoading = false
  }
}
const onReset = () => {
  data.value = clone(props.modelValue)
}

let incidents: any[] = $ref([])
const addIncident = async (incidentNumber: string) => {
  try {
    const result: any = await calculationService.newIncident(incidentNumber)
    const { id, number } = result
    return { id, number, description: number }
  }
  catch (error) {
    printError('ERROR ON LOAD INCIDENSTS:', error)
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
  loadIncidents()
})
</script>

<template>
  <AnalisysSheet
    v-model:editing="isEditing"
    v-model:loading="isLoading"
    :name="name"
    title="Ficha de Análise"
    :subtitle="title"
    @reset="onReset"
    @submit.prevent="onSubmit"
  >
    <div class="pt-6 max-w-200 m-x-auto flex flex-col gap-4">
      <div class="pb-2 font-bold text-md">
        Créditos
      </div>
      <div v-for="(value, index) in data as any[]" :key="index" class="grid gap-x-3 grid-cols-[3fr_3fr_1fr_232px_40px]">
        <InputSelect
          v-model="value.incidentId"
          v-model:options="incidents"
          label="Número de Incidente"
          mask="#######-##.####.#.##.####"
          :to-add="addIncident"
          :rules="[(value: any) => !!value || 'É um campo obrigatório']"
          :disable="!isEditing"
        />
        <QInput
          v-model="value.coins.value"
          label="Valor"
          outlined
          dense
          :disable="!isEditing"
          type="number"
        />
        <QSelect
          v-model="value.coins.coin"
          label="Moeda"
          :disable="!isEditing"
          :options="options?.coinOptions"
          option-label="legend"
          option-value="id"
          emit-value
          map-options
          outlined
          dense
        />
        <QSelect
          v-model="value.classes.classe" label="Classe"
          :disable="!isEditing"
          :options="options?.classesOptions"
          option-label="legend"
          option-value="id"
          emit-value
          map-options
          outlined
          dense
        />
        <div
          class="cursor-pointer bg--error h-10 w-10 rounded-.5 border-1 border-red-8 flex justify-center items-center"
          :disabled="!isEditing ? true : value.id ? true : undefined"
          @click="removeCredit(!value.id && index)"
        >
          <div class="i-carbon-trash-can bg-white" />
        </div>
      </div>
      <Btn
        label="Adicionar novo Crédito"
        icon="i-carbon-add"
        :disabled="!isEditing"
        type="button"
        @click="addNewCredit"
      />
    </div>
  </AnalisysSheet>
</template>
