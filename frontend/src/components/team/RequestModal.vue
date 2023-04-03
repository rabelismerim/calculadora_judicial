<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  users?: any[]
}>(), {
  users: () => ([]),
})
const emit = defineEmits(['update:model-value'])

let loading = $ref(false)
const tab = $ref('pending')
const pendingUsers = computed(() => props.users.filter(({ status }) => status.toLowerCase() === 'p'))
const rejectedUsers = computed(() => props.users.filter(({ status }) => status.toLowerCase() === 'r'))

const onAuthorize = async (user: any) => {
  const { id } = user
  loading = true
  try {
    // const result = await usersService.requestAccess()
  }
  catch (error) {
    printError('ERROR ON ACCEPTING THE USER REQUEST:', error)
  }
  finally {
    loading = false
  }
}
const onReject = async (user: any) => {
  const { id } = user
  loading = true
  try {
    // const result = await usersService.requestAccess()
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
    title="Solicitações"
    modal-class="max-w-120"
    :close-disabled="loading"
    class="request-modal"
    @close="emit('update:model-value', false)"
  >
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
            />
            <Btn
              label="Aceitar"
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
        >
          <UserCell :model-value="user" />
          <div class="flex flex-1 justify-end gap-2">
            <Btn
              label="Aceitar"
            />
          </div>
        </div>
      </QTabPanel>
    </QTabPanels>
  </Modal>
</template>

<style>
.request-modal .q-tab__content {
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 8px;
}
</style>
