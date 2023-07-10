<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  users?: any[]
}>(), {
  users: () => ([]),
})
const emit = defineEmits(['update:model-value', 'success'])

const { hasPermissions } = $user

const form = ref(null as any)

let loading = $ref(false)
let editingUser: any = $ref({})
let tab = $ref('pending')
const pendingUsers = computed(() => props.users.filter(({ status }) => status.toLowerCase() === 'p'))
const rejectedUsers = computed(() => props.users.filter(({ status }) => status.toLowerCase() === 'r'))

let permissionOptions: any[] = $ref([])
const subareaOptions: any[] = [
  { description: 'Sócio', id: 'S' },
  { description: 'Gerente', id: 'G' },
  { description: 'Diretor', id: 'D' },
  { description: 'Analista', id: 'A' },
  { description: 'Consultor Sênior', id: 'C' },
]

const editUser = (user: any) => {
  const { id, picture, fullName, email, groups, role } = user
  if (email)
    editingUser = { id, picture, fullName, email, role, group: groups[0] }
}
const clear = () => {
  emit('update:model-value', false)
  tab = 'pending'
  editingUser = {}
}
const onAuthorize = async () => {
  const isValid = await form.value.validate()
  if (!isValid)
    return
  const { email, group, role } = editingUser
  loading = true
  try {
    const result = await usersService.setPermission({ email, groups: [group], role, status: 'A' })
    const { status } = result
    if (status) {
      clear()
      emit('success')
    }
  }
  catch (error) {
    printError('ERROR ON ACCEPTING THE USER REQUEST:', error)
  }
  finally {
    loading = false
  }
}
const onReject = async (user: any) => {
  if (!user?.email)
    return
  loading = true
  await delay(3)
  try {
    const result = await usersService.setPermission({ email: user.email, status: 'R' })
    const { status } = result
    if (status)
      clear()
  }
  catch (error) {
    printError('ERROR ON REJECTING THE USER REQUEST:', error)
  }
  finally {
    loading = false
  }
}
onMounted(async () => {
  try {
    if (!hasPermissions('can_authorize_users', 'view_group'))
      return
    permissionOptions = await usersService.getGroups()
  }
  catch (error) {
    printError('ERROR ON LOADING GROUPS:', error)
  }
})
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="editingUser ? 'Cadastrar Usuário' : 'Solicitações'"
    modal-class="max-w-120"
    :close-disabled="loading"
    :loading="loading"
    class="request-modal"
    @close="clear"
  >
    <div v-if="editingUser?.email">
      <QForm
        ref="form"
        @submit="onAuthorize"
      >
        <div class="max-h-100 overflow-y-auto px-6 pt-4">
          <div class="flex mb-6">
            <UserCell :model-value="editingUser" />
          </div>
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
          <Btn
            label="Voltar"
            outlined
            type="button"
            @click="editingUser = {}"
          />
          <Btn
            label="Cadastrar"
          />
        </div>
      </QForm>
    </div>
    <div v-else>
      <QTabs
        v-model="tab"
        align="left"
        active-color="secondary"
      >
        <QTab
          name="pending"
          label="Pendentes"
        >
          <span class="bg--secondary/12 color--secondary rounded-full px-2 font-bold">
            {{ pendingUsers.length }}
          </span>
        </QTab>
        <QTab
          name="rejected"
          label="Ignoradas"
        />
      </QTabs>
      <QTabPanels v-model="tab" animated class="shadow-2 rounded-borders">
        <QTabPanel name="pending">
          <div
            v-if="pendingUsers.length === 0"
            class="pa-4 text-center"
          >
            Sem Usuários Pendentes no momento...
          </div>
          <div
            v-for="(user, pendingIndex) in pendingUsers"
            v-else
            :key="user.id"
            class="flex py-3"
            :class="{ 'border-b-1 border--black/12': pendingIndex < pendingUsers.length - 1 }"
          >
            <UserCell :model-value="user" />
            <div class="flex flex-1 justify-end gap-2">
              <Btn
                label="Ignorar"
                outlined
                :disabled="loading"
                @click="onReject(user)"
              />
              <Btn
                label="Aceitar"
                :disabled="loading"
                @click="editUser(user)"
              />
            </div>
          </div>
        </QTabPanel>

        <QTabPanel name="rejected">
          <div
            v-if="rejectedUsers.length === 0"
            class="pa-4 text-center"
          >
            Sem Usuários Ignorados no momento...
          </div>
          <div
            v-for="(user, rejectedIndex) in rejectedUsers"
            v-else
            :key="user.id"
            class="flex py-3"
            :class="{ 'border-b-1 border--black/12': rejectedIndex < rejectedUsers.length - 1 }"
            @click="onReject"
          >
            <UserCell :model-value="user" />
            <div class="flex flex-1 justify-end gap-2">
              <Btn
                label="Aceitar"
                :disabled="loading"
                @click="editUser(user)"
              />
            </div>
          </div>
        </QTabPanel>
      </QTabPanels>
    </div>
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
