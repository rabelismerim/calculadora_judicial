<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: any
  title: string
  name: number
  defaultValue?: any
}>(), {
  defaultValue: () => ({}),
})
const $emit = defineEmits(['update:model-value'])

let isLoading = $ref(false)
let isEditing = $ref(false)

const newCredit = { value: 0, coin: 'R', class: 'I' }
let localData = $ref({
  values: [clone(newCredit)],
} as any)
const data = computed({
  get() {
    return localData
  },
  set(newValue) {
    localData = newValue
  },
})
const addNewCredit = () => {
  if (!isEditing)
    return
  data.value.values.push({ value: 0, coin: 'Real', class: '1' })
}
const removeCredit = (id: number) => {
  if (!isEditing)
    return
  data.value.values.splice(id, 1)
}
const onSubmit = async () => {
  isLoading = true
  try {
    // const result = await creditorsService.setNotice(data.value)
    // console.warn(result)
    isEditing = false
  }
  catch (error) {
    printError('ERROR ON SUBMIT RECOVERING NOTICE:', error)
  }
  finally {
    isLoading = false
  }
}
const onReset = () => {
  data.value.values = [clone(newCredit)]
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
      <InputText v-model="data.description" label="Descrição" :disable="!isEditing" />
      <div class="pb-2 font-bold text-md">
        Créditos
      </div>
      <div v-for="(value, index) in data.values as any[]" :key="index" class="grid gap-x-3 grid-cols-[3fr_1fr_1fr_40px]">
        <QInput v-model="value.value" label="Valor" outlined dense :disable="!isEditing" />
        <InputSelect v-model="value.coin" label="Moeda" :disable="!isEditing" :options="[{ description: 'Real', id: 'R' }, { description: 'Dólar', id: 'D' }]" />
        <InputSelect v-model="value.class" label="Classe" :disable="!isEditing" :options="[{ description: 'Classe I', id: '1' }, { description: 'Classe II', id: '2' }, { description: 'Classe III', id: '3' }]" />
        <div class="cursor-pointer bg--error h-10 w-10 rounded-.5 border-1 border-red-8 flex justify-center items-center" :disabled="!isEditing ? true : undefined" @click="removeCredit(index)">
          <div class="i-carbon-trash-can bg-white" />
        </div>
      </div>
      <Btn label="Adicionar novo Crédito" icon="i-carbon-add" :disabled="!isEditing" type="button" @click="addNewCredit" />
    </div>
  </AnalisysSheet>
</template>
