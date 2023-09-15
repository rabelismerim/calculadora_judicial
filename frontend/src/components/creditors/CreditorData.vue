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

let editingCreditor = $ref({
  legalNumber: '',
  admission: null,
  dismissal: null,
  fine: null,
  defaultInterest: null,
  advocativeHours: null,
  occurrence: null,
})

const onReset = () => {
  editingCreditor = clone(props.modelValue)
}

watchEffect(() => editingCreditor = clone(props.modelValue))

const onSubmit = async () => {
  isLoading = true
  try {
    // const result = await creditorsService.setCreditorClaim(payload)
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
        Ficha do Credor
      </div>
      <div class="grid sm:grid-cols-2 gap-2">
        <InputDate
          v-if="isValidCPF(editingCreditor.legalNumber)"
          v-model="editingCreditor.admission"
          label="Data de Admissão"
        />
        <InputDate
          v-if="isValidCPF(editingCreditor.legalNumber)"
          v-model="editingCreditor.dismissal"
          label="Data de Demissão"
        />
        <InputNumber
          v-model="editingCreditor.fine"
          label="Multa"
        />
        <InputNumber
          v-model="editingCreditor.defaultInterest"
          label="Juros Moratórios"
        />
        <InputNumber
          v-model="editingCreditor.advocativeHours"
          label="Horários Advocatícios"
        />
        <QSelect
          v-model="editingCreditor.occurrence"
          label="Ocorrência"
          :options="options.occurrenceOptions"
          dense
          outlined
          map-options
          emit-value
          option-label="legend"
          option-value="id"
        />
      </div>
    </div>
  </AnalisysSheet>
</template>
