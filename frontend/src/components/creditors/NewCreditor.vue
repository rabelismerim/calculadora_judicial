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
  }
}>(), {
  modelValue: false,
  options: () => ({ recoverings: [] }),
})
const emit = defineEmits(['update:modelValue', 'update:creditor', 'success'])

let loading = $ref(false)
const form = ref(null as any)

const mappedRecoverings = $computed(() => props.options.recoverings
  .map(({ id, entity: { name } }: any) => ({ name, id })))

const nullCreditor: Creditor = {
  name: '',
  legalNumber: '',
  description: '',
  recoverings: [],
}
let creatingCreditor: Creditor = $ref(clone(nullCreditor))

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
              v-model="creatingCreditor.recoverings"
              label="Recuperandas"
              outlined
              emit-value
              map-options
              option-label="name"
              option-value="id"
              multiple
              :options="mappedRecoverings"
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
