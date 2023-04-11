<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  users?: any[]
}>(), {
  users: () => ([]),
})
const emit = defineEmits(['update:model-value'])

let loading = $ref(false)
let editingUser: any = $ref({})
const tab = $ref('pending')
const pendingUsers = computed(() => props.users.filter(({ status }) => status.toLowerCase() === 'p'))
const rejectedUsers = computed(() => props.users.filter(({ status }) => status.toLowerCase() === 'r'))

const editUser = (user: any) => {
  if (user.email)
    editingUser = clone(user)
}
const onAuthorize = async () => {
  const { email, groups } = editingUser
  loading = true
  try {
    const result = await usersService.setPermission({ email, groups, isActive: true })
    console.warn(result)
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
    const result = await usersService.setPermission({ email: user.email, isActive: false })
    console.warn(result)
  }
  catch (error) {
    printError('ERROR ON REJECTING THE USER REQUEST:', error)
  }
  finally {
    loading = false
  }
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="editingUser ? 'Cadastrar Usuário' : 'Solicitações'"
    modal-class="max-w-120"
    :close-disabled="loading"
    :loading="loading"
    class="request-modal"
    @close="emit('update:model-value', false)"
  >
    <div v-if="editingUser?.email">
      <pre>{{ editingUser }}</pre>
      <div class="flex justify-end gap-3 p-4 border-t-1 border-black/12">
        <Btn
          label="Voltar"
          outlined
          @click="editingUser = {}"
        />
        <Btn
          label="Cadastrar"
          @click="onAuthorize"
        />
      </div>
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
            v-for="(user, pendingIndex) in pendingUsers"
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
            v-for="(user, rejectedIndex) in rejectedUsers"
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
