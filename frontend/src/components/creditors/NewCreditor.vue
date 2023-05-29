<script setup lang='ts'>
interface Creditor {
  name: string
  legalNumber: string
  recoverings: any[]
}
const props = withDefaults(defineProps<{
  modelValue: boolean
  creditor: Creditor
  options: {
    recoverings: any[]
    rates: any[]
  }
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue', 'update:creditor', 'success'])

let loading = $ref(false)
const form = ref(null) as any

const nullRecovering = { recoveringId: null, rateId: null }
let newRecovering = $ref(clone(nullRecovering))

const freeRecoverings = computed(() => props.options.recoverings
  .filter(({ id }: any) => !props.creditor?.recoverings
    ?.map(({ recoveringId }: any) => recoveringId)?.includes(id))
  .map(({ id: value, entity: { name: label } }) => ({ label, value })))
const addRecovering = () => {
  const { recoverings } = props.creditor
  if (!newRecovering.recoveringId || !newRecovering.rateId) {
    throwError({ message: 'Você precisa adicionar uma recuperanda e uma taxa!', id: 'NEW_RECOVERING' })
    return
  }
  const newCreditor = {
    ...props.creditor,
    recoverings: [...recoverings, clone(newRecovering)],
  }
  emit('update:creditor', newCreditor)
  newRecovering = clone(nullRecovering)
}
const rates = computed(() => props.options.rates
  .map(({ id: value, index: label }) => ({ label, value })))

const nullCreditor: Creditor = {
  name: '',
  legalNumber: ' ',
  recoverings: [],
}
const newCreditor = computed({
  get() {
    return props.creditor
  },
  set(value: any) {
    emit('update:creditor', value)
  },
})
const removeRecovering = (index: number) => {
  const creditor = clone(newCreditor.value)
  creditor.recoverings.splice(index, 1)
  newCreditor.value = creditor
}
const clear = async () => {
  newCreditor.value = clone(nullCreditor)
  await delay(0.1)
  form.value.reset()
}
const onSubmit = async () => {
  if (newCreditor.value.id)
    return
  const isValid = await form.value.validate()
  if (!isValid)
    return
  if (newCreditor.value.recoverings.length <= 0) {
    throwError({ message: 'Precisa de no mínimo uma Recuperanda selecionada!' })
    return
  }
  loading = true
  try {
    const result: any = await creditorsService.newCreditors(newCreditor.value)
    if (result.filter((item: any) => !!item).length > 0) {
      notify({ message: `Credor ${newCreditor.value.name} foi criado com sucesso!` })
      clear()
      emit('update:modelValue', false)
      emit('success')
    }
  }
  catch (error) {
    printError('ERROR ON CREATE NEW CREDITOR:', error)
  }
  finally {
    loading = false
  }
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="newCreditor?.id ? `Editar Credor: ${newCreditor.name}` : 'Cadastro de Credor'"
    hint="Vincular o Novo Credor às Recuperandas do Projeto."
    modal-class="max-w-200"
    @update:model-value="(value: boolean) => emit('update:modelValue', value)"
    @close="clear"
  >
    <QForm ref="form" @submit="onSubmit">
      <div class="grid sm:grid-cols-2 gap-x-6 gap-y-2 px-6 py-3">
        <InputText
          v-model="newCreditor.name"
          label="Nome do Credor"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          grow
        />
        <InputLegal
          v-model="newCreditor.legalNumber"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          grow
        />
        <div class="col-span-2">
          <div class="flex gap-4 mb-4">
            <QSelect
              v-model="newRecovering.recoveringId"
              label="Recuperanda"
              outlined
              emit-value
              map-options
              :options="freeRecoverings"
              class="flex-1"
            >
              <template #no-option>
                <QItem>
                  <QItemSection class="text-grey">
                    Não existe Recuperanda Cadastrada
                  </QItemSection>
                </QItem>
              </template>
            </QSelect>
            <QSelect
              v-model="newRecovering.rateId"
              label="Taxa"
              outlined
              emit-value
              map-options
              :options="rates"
              class="flex-1"
            >
              <template #no-option>
                <QItem>
                  <QItemSection class="text-grey">
                    Não existe Recuperanda Cadastrada
                  </QItemSection>
                </QItem>
              </template>
            </QSelect>
            <Btn
              label="Adicionar"
              icon="i-carbon-add"
              type="button"
              @click="addRecovering"
            />
          </div>
          <div
            v-for="({ recoveringId, rateId }, index) in newCreditor.recoverings as any[]"
            :key="recoveringId"
            class="flex gap-4 py-1 items-center"
          >
            <div>
              {{ options.recoverings.find(({ id }) => id === recoveringId)?.entity?.name }}
              - {{ options.rates.find(({ id }) => id === rateId)?.index }}
            </div>
            <button type="button" class="color--error hover:bg--error/12 rounded p-2" @click="removeRecovering(index)">
              <div class="i-carbon-trash-can" />
            </button>
          </div>
        </div>
      </div>
      <div class="relative flex justify-end gap-2 p-3 border-t-1 ">
        <QLinearProgress
          v-if="loading"
          indeterminate
          color="secondary"
          class="absolute top-0 left-0"
          size="xs"
        />
        <Btn
          label="Cadastrar"
          type="button"
          :loading="loading"
          loading-label="Criando Projeto..."
          :disabled="!!newCreditor.id"
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
