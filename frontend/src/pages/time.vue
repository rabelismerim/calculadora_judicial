<script setup lang="ts">
const router = useRouter()

const filterBy = $ref('')
let loading = $ref(false)
const showingRequests = $ref(false)
const mode = $ref('person')
let users: any[] = $ref([])
let projects: any[] = $ref([])
const mapProjects = computed(() => projects.map((project) => {
  const newProject = clone(project)
  const { id, description, projectUsers, status, statusDisplay } = newProject
  const filterBy = (toCompare: string) => ({ groups }: any) => groups.findIndex(({ name }: any) => name === toCompare)
  const mapUser = ({ firstName, lastName, userpicture, username, groups }: any) => ({
    fullName: `${firstName} ${lastName}`,
    picture: userpicture,
    email: `${username}@deloitte.com`,
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

const tab = $ref('all')
const pendingRequests = computed(() => users.filter(({ isActive }) => !isActive).length)

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
        label="Solicitações"
        icon="i-carbon-request-quote"
        disabled
        @click="showingRequests = true"
      />
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
      :items="users"
      :loading="loading"
    />

    <template #out>
      <Modal
        v-model="showingRequests"
        title="Solicitações"
        modal-class="max-w-120"
        :close-disabled="loading"
      >
        content...
      </Modal>
    </template>
  </Page>
</template>

<route lang="yaml">
meta:
  permissions: [view_user]
</route>
