<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  history: any[]
  options: any
  calculation?: any
  status?: string
  specialApprovers?: any[]
}>(),
{
  modelValue: false,
  history: () => ([]),
  specialApprovers: () => ([]),
  calculation: () => ({
    specialApprovers: [],
  }),
})
const emit = defineEmits(['update:modelValue', 'updateStatus'])
let step = $ref('history')

let loading = $ref(false)

const getUser = (username: string) => props.options?.users
  ?.find((user: any) => username === user.username)

const avatar = (username: string) => {
  const host = import.meta.env.VITE_API_HOST
  const { pictureUrl, userpicture } = getUser(username) || {}
  const userImage = pictureUrl
    ? `${host}/juca${pictureUrl}`
    : userpicture
      ? `data:image/jpg;base64,${userpicture}`
      : undefined
  return userImage
}

const label = ({ type, createUser }: any = {}) => {
  if (type === 'historical')
    return `Campo alterado por ${getUser(createUser)?.fullName || ''}`
  if (type === 'step')
    return `Status alterado por ${getUser(createUser)?.fullName || ''}`
  return ''
}

const statusDefault = {
  nextStep: undefined,
  comment: '',
}
let editingStep = $ref(clone(statusDefault))

const clear = async () => {
  emit('update:modelValue', false)
  await delay(0.2)
  editingStep = clone(statusDefault)
  step = 'history'
}

const form = ref(null as any)
const onSubmit = async () => {
  const isValid = await form.value.validate()
  if (!props.calculation?.id || !isValid)
    return

  loading = true
  try {
    await calculationService.changeStep(editingStep, props.calculation?.id)
    clear()
    emit('updateStatus')
    notify({ message: 'O Status do Cálculo foi alterado com sucesso!' })
  }
  catch (error) {
    printError('ERROR ON CHANGING STATUS:', error)
  }
  finally {
    loading = false
  }
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="step === 'history' ? 'Histórico do Cálculo' : 'Alterar Status'"
    :hint="step === 'history' ? 'Histórico de processos internos do Cálculo' : 'Para alterar Status defina o novo Status do Cálculo.'"
    modal-class="max-w-160"
    @close="clear"
  >
    <QTabPanels v-model="step" animated>
      <QTabPanel name="history">
        <div class="max-h-100">
          <QTimeline v-if="history?.length > 0" color="primary" layout="comfortable">
            <QTimelineEntry
              v-for="{ createdAt, createUser, type, ...rest } in history"
              :key="createdAt"
              :subtitle="formatDateHour(createdAt)"
              :avatar="avatar(createUser)"
            >
              <template #title>
                <div class="font-bold text-lg">
                  {{ label({ ...rest, type, createUser }) }}
                </div>
              </template>
              <div>
                <div v-if="type === 'historical'">
                  <div>
                    O Campo <span class="bg-gray-2 rounded px-2">{{ rest?.fieldChangedDisplay }}</span>
                  </div>
                  <div>
                    Mudou de <span class="bg-gray-2 rounded px-2">{{ rest?.previousValue || 'Nulo' }}</span>
                    para <span class="bg-gray-2 rounded px-2">{{ rest?.currentValue?.toString() || 'Nulo' }}</span>
                  </div>
                </div>
                <div v-if="type === 'step'">
                  <div>
                    Status do Cálculo foi alterado para <span class="bg-gray-2 rounded px-2">{{ rest?.stepDisplay }}</span>
                  </div>
                  <div>
                    <div class="font-bold mt-2 text-grey-9">
                      Comentários:
                    </div>
                    <div v-for="comment in rest.comments as any[]" :key="comment.id">
                      {{ comment?.text }}
                    </div>
                  </div>
                </div>
              </div>
            </QTimelineEntry>
          </QTimeline>
          <div v-else class="p-8 text-center">
            Nenhum item no Histórico deste Cálculo...
          </div>
        </div>
      </QTabPanel>

      <QTabPanel name="status">
        <QForm ref="form" @submit="onSubmit">
          <div class="text-h6">
            <CalculationFluxogram
              :status="status"
              class="mb-5"
            />
            <div v-if="calculation?.step === 'B'" class="text-sm mb-4">
              <div class="font-bold mb-2">
                Aprovadores Especiais
              </div>
              <div
                v-for="approver in calculation.specialApprovers as any[]"
                :key="approver.id"
                class="flex gap-2 items-center mb-2"
              >
                <UserPicture
                  v-model="approver.projectUser"
                  class="h-7 w-7"
                />
                <div>{{ approver?.projectUser?.fullName }}</div>
                <StatusTag
                  :label="approver?.approved ? 'Aprovou' : 'Aguardando aprovação...'"
                  :color="approver?.approved ? '#87bc24' : '#c4d600'"
                />
              </div>
            </div>
            <QSelect
              v-model="editingStep.nextStep"
              label="Enviar para Status"
              :disable="loading || !calculation?.id"
              :options="options?.steps"
              option-label="legend"
              option-value="id"
              emit-value
              map-options
              outlined
              dense
              :rules="[(value: any) => !!value || 'Este campo é obrigatório!']"
            >
              <template #no-option>
                <div class="p-3 text-center">
                  Você não tem permissão para alterar o Status do Cálculo no momento.
                </div>
              </template>
            </QSelect>
            <InputUsers
              v-if="editingStep.nextStep === 'B'"
              v-model="editingStep.specialApprovers"
              label="Aprovadores Especiais"
              value-key="idUser"
              :users="specialApprovers"
              :rules="[(value: any) => value?.length > 0 || 'Este campo é obrigatório!']"
            />
            <QInput
              v-model="editingStep.comment"
              label="Comentário"
              :disable="loading || !calculation?.id"
              outlined
              type="textarea"
              :rules="[(value: any) => !!value || 'Este campo é obrigatório!']"
            />
          </div>
        </QForm>
      </QTabPanel>
    </QTabPanels>
    <div v-if="step === 'history'" class="flex justify-end gap-4 p-4 border-1 border-t-black/12">
      <Btn label="Fechar" outlined @click="clear" />
      <Btn label="Alterar Status" @click="step = 'status'" />
    </div>
    <div v-else class="relative flex justify-end gap-4 p-4 border-1 border-t-black/12">
      <QLinearProgress
        v-if="loading"
        indeterminate
        color="secondary"
        class="absolute top-0 left-0"
        size="xs"
      />
      <Btn label="Voltar" outlined @click="step = 'history'" />
      <Btn label="salvar" :disabled="loading || !props.calculation?.id" :loading="loading" @click="onSubmit" />
    </div>
  </Modal>
</template>
