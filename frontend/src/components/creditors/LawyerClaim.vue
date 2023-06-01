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
  coins: {
    coin: 'B',
    value: 0,
  },
}
let localData = $ref(clone(newCredit) as any)
const data = computed({
  get() {
    return localData
  },
  set(newValue) {
    localData = newValue
  },
})
watchEffect(() => data.value = clone(props.modelValue || newCredit))

const onSubmit = async () => {
  isLoading = true
  try {
    const payload = { ...data.value, creditorId: props.creditorId }
    await creditorsService.setLawyerClaim(payload)
    isEditing = false
    emit('save')
  }
  catch (error) {
    printError('ERROR ON SUBMIT LAWYER CLAIM:', error)
  }
  finally {
    isLoading = false
  }
}
const onReset = () => {
  data.value = clone(props.modelValue || newCredit)
}
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
    <div class="pt-6 max-w-200 m-x-auto">
      <div class="pb-2 font-bold text-md">
        Crédito
      </div>
      <div class="grid gap-x-3 grid-cols-[3fr_1fr]">
        <QInput v-model="data.coins.value" label="Valor" outlined dense :disable="!isEditing" />
        <QSelect
          v-model="data.coins.coin"
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
      </div>
    </div>
  </AnalisysSheet>
</template>
