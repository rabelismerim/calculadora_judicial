<script setup lang="ts">
const { hasPermissions } = $user

const tab = $ref('all')
const filterBy = $ref('')
let loading = $ref(false)
const showingRequests = $ref(false)
const mode = $ref('person')
let users: any[] = $ref([])
let projects: any = $ref([])

const mapProjects = computed(() => projects.map((project: any) => {
  const newProject = clone(project)
  const { id, description, projectUsers, status, statusDisplay } = newProject
  const filterBy = (toCompare: string) => ({ groups }: any) => groups?.findIndex(({ name }: any) => name === toCompare)
  const mapUser = ({ firstName, lastName, pictureUrl, userpicture, username, email, groups }: any) => ({
    fullName: `${firstName} ${lastName}`,
    pictureUrl,
    userpicture,
    email: email || (username?.includes('@') ? username : ''),
    groups,
  })
  const users = projectUsers.map(mapUser)
  const executors = users.filter(filterBy('Executor'))
  const approvers = users.filter(filterBy('Aprovador'))
  const revisors = users.filter(filterBy('Revisor'))
  return {
    id,
    description,
    executors,
    approvers,
    revisors,
    status,
    statusDisplay,
  }
}))
const activeUsers = computed(() => users.filter(({ status }) => ['A', 'F', 'I'].includes(status)))
const pendingUsers = computed(() => users.filter(({ status }) => ['P', 'R'].includes(status)))
const pendingUsersCount = computed(() => users.filter(({ status }) => status === 'P').length)

let showEditUser = $ref(false)
let editingUser = $ref({})
const onEditUser = (user: any) => {
  showEditUser = true
  editingUser = user
}

const loadPage = async () => {
  loading = true
  try {
    users = await usersService.getUsers()
    projects = await projectService.getProjects()
  }
  catch (error) {
    printError('ERROR ON LOAD REQUEST OPTIONS:', error)
  }
  finally {
    loading = false
  }
}
onMounted(() => loadPage())
</script>

<template>
  <Page>
    <Header title="Time">
      <template #side>
        <ReloadBtn
          hint="Recarregar a Lista de Usuários"
          @click="loadPage"
        />
      </template>

      <BtnToggle
        v-model="mode"
        :items="[
          { label: 'Modo Pessoas', value: 'person' },
          { label: 'Modo Projetos', value: 'project' },
        ]"
      />
      <Btn
        v-if="hasPermissions('can_authorize_users')"
        label="Solicitações"
        :icon="pendingUsersCount === 0 ? 'i-carbon-request-quote' : ''"
        @click="showingRequests = true"
      >
        <span
          v-if="pendingUsersCount > 0"
          class="bg-white color--primary rounded-full px-1.5 text-sm"
        >
          {{ pendingUsersCount }}
        </span>
      </Btn>
    </Header>

    <TeamProjectsTable
      v-if="mode === 'project'"
      v-model:tab="tab"
      v-model:filter="filterBy"
      :items="mapProjects"
      :loading="loading"
    />
    <PeopleTable
      v-if="mode === 'person'"
      v-model:tab="tab"
      v-model:filter="filterBy"
      :items="activeUsers"
      :loading="loading"
      @editing-user="onEditUser"
    />

    <template #out>
      <EditUser
        v-model="showEditUser"
        :user="editingUser"
        @success="loadPage"
      />

      <RequestModal
        v-model="showingRequests"
        :users="pendingUsers"
        @success="loadPage"
      />
    </template>
  </Page>
</template>

<route lang="yaml">
meta:
  permissions: [view_user]
</route>
