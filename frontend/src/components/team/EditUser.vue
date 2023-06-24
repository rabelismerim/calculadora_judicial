<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  user?: any
}>(), {
  user: () => ({}),
})
const emit = defineEmits(['update:model-value', 'success'])

const form = ref(null as any)

let loading = $ref(false)
let editingUser: any = $ref({})
watchEffect(() => {
  editingUser = clone(props.user)
  editingUser.group = editingUser.groups?.[0]?.id
})
let tab = $ref('pending')

let permissionOptions: any[] = $ref([])
let statusOptions: any[] = $ref([])

const subareaOptions: any[] = [
  { description: 'Sócio', id: 'S' },
  { description: 'Gerente', id: 'G' },
  { description: 'Diretor', id: 'D' },
  { description: 'Analista', id: 'A' },
  { description: 'Consultor Sênior', id: 'C' },
]

const clear = () => {
  emit('update:model-value', false)
  tab = 'pending'
  editingUser = {}
}
const onEdit = async () => {
  const isValid = await form.value.validate()
  if (!isValid)
    return
  const { email, group, role, status } = editingUser
  loading = true
  try {
    const result = await usersService.setPermission({ email, groups: [group], role, status })
    const { status: userStatus } = result
    if (userStatus) {
      clear()
      emit('success')
      notify({ message: 'O Usuário foi alterado com sucesso!' })
    }
  }
  catch (error) {
    printError('ERROR ON ACCEPTING THE USER REQUEST:', error)
  }
  finally {
    loading = false
  }
}

onMounted(async () => {
  try {
    permissionOptions = await usersService.getGroups()
    const options = await creditorsService.getOptions()
    statusOptions = options.userStatusOptions
      ?.map(({ id, legend }: any) => ({ id, description: legend }))
  }
  catch (error) {
    printError('ERROR ON LOADING GROUPS:', error)
  }
})
</script>

<template>
  <Modal
    :model-value="modelValue"
    title="Editando Usuário"
    modal-class="max-w-120"
    :close-disabled="loading"
    :loading="loading"
    class="request-modal"
    @close="clear"
  >
    <QForm
      ref="form"
      @submit="onEdit"
    >
      <div class="max-h-100 overflow-y-auto px-6 pt-4">
        <div class="flex mb-6">
          <UserCell :model-value="editingUser" />
        </div>
        <InputSelect
          v-model="editingUser.status"
          label="Status"
          :rules="[(value: any) => !!value || 'Este campo é obrigatório!']"
          :options="statusOptions"
        />
        <InputSelect
          v-model="editingUser.group"
          label="Permissão"
          :rules="[(value: any) => !!value || 'Este campo é obrigatório!']"
          :options="permissionOptions"
        />
        <InputSelect
          v-model="editingUser.role"
          label="Cargo"
          :rules="[(value: any) => !!value || 'Este campo é obrigatório!']"
          :options="subareaOptions"
        />
      </div>
      <div class="flex justify-end gap-3 p-4 border-t-1 border-black/12">
        <btn
          type="submit"
          label="Salvar"
        />
      </div>
    </QForm>
  </Modal>
</template>

<style>
.request-modal .q-tab__content {
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 8px;
}
.request-modal .q-tab-panels {
  box-shadow: none;
}
</style>
