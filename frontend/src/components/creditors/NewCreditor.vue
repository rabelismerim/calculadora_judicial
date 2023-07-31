<script setup lang='ts'>
interface Creditor {
  name: string
  legalNumber: string
  description: string
  recoverings: any[]
}
const props = withDefaults(defineProps<{
  modelValue: boolean
  options: {
    recoverings: any[]
    rates: any[]
  }
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue', 'update:creditor', 'success'])

let loading = $ref(false)
const form = ref(null as any)

const nullCreditor: Creditor = {
  name: '',
  legalNumber: '',
  description: '',
  recoverings: [],
}
let creatingCreditor: Creditor = $ref(clone(nullCreditor))

const nullRecovering = { recoveringId: null, rateId: null }
let newRecovering = $ref(clone(nullRecovering))

const freeRecoverings = computed(() => props.options.recoverings
  ?.filter(({ id }: any) => !creatingCreditor?.recoverings
    ?.map(({ recoveringId }: any) => recoveringId)?.includes(id))
  ?.map(({ id: value, entity: { name: label } }) => ({ label, value })))
const addRecovering = () => {
  const { recoverings } = clone(creatingCreditor)
  if (!newRecovering.recoveringId || !newRecovering.rateId) {
    throwError({ message: 'Você precisa adicionar uma recuperanda!', id: 'NEW_RECOVERING' })
    return
  }
  creatingCreditor.recoverings = [...recoverings, clone(newRecovering)]
  newRecovering = clone(nullRecovering)
}

const removeRecovering = (index: number) => {
  const newCreditor = clone(creatingCreditor)
  newCreditor.recoverings.splice(index, 1)
  creatingCreditor = newCreditor
}
const clear = async () => {
  creatingCreditor = clone(nullCreditor)
  await delay(0.1)
  form.value.reset()
}
const onSubmit = async () => {
  const isValid = await form.value.validate()
  if (!isValid)
    return
  if (creatingCreditor.recoverings.length <= 0) {
    throwError({ message: 'Precisa de no mínimo uma Recuperanda selecionada!' })
    return
  }
  loading = true
  try {
    const result: any = await creditorsService.newCreditors(creatingCreditor as any)
    if (result?.filter((item: any) => !!item).length > 0) {
      notify({ message: `Credor ${creatingCreditor.name} foi criado com sucesso!` })
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
    title="Cadastro de Credor"
    hint="Vincular o Novo Credor às Recuperandas do Projeto."
    modal-class="max-w-200"
    @update:model-value="(value: boolean) => emit('update:modelValue', value)"
    @close="clear"
  >
    <QForm ref="form" @submit="onSubmit">
      <div class="grid sm:grid-cols-2 gap-x-6 gap-y-2 px-6 py-3">
        <InputText
          v-model="creatingCreditor.name"
          label="Nome do Credor"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          grow
        />
        <InputLegal
          v-model="creatingCreditor.legalNumber"
          :rules="[(value: any) => !!value || 'Este é um campo obrigatório!']"
          grow
        />
        <QInput
          v-model="creatingCreditor.description"
          label="Descrição"
          outlined
          type="textarea"
          rows="3"
          class="mb-5 col-span-2"
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

            <Btn
              label="Adicionar"
              icon="i-carbon-add-filled"
              type="button"
              @click="addRecovering"
            />
          </div>
          <div v-if="creatingCreditor.recoverings.length > 0" class="font-bold text-lg">
            Recuperandas Selecionadas
          </div>
          <div
            v-for="({ recoveringId, rateId }, index) in creatingCreditor.recoverings as any[]"
            :key="recoveringId"
            class="flex gap-4 py-1 items-center"
          >
            <div>
              {{ options.recoverings?.find(({ id }) => id === recoveringId)?.entity?.name }}
              - {{ options.rates?.find(({ id }) => id === rateId)?.index }}
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
          :disabled="loading"
          @click="onSubmit"
        />
      </div>
    </QForm>
  </Modal>
</template>
