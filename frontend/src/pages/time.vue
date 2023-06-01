<script setup lang="ts">
const router = useRouter()

const tab = $ref('all')
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
const activeUsers = computed(() => users.filter(({ status }) => ['A', 'F', 'I'].includes(status)))
const pendingUsers = computed(() => users.filter(({ status }) => ['P', 'R'].includes(status)))
const pendingUsersCount = computed(() => users.filter(({ status }) => status === 'P').length)
const projectsPerUser: any = computed(() => projects?.reduce((acc, project) => {
  const { id, description, projectUsers, engagement } = project
  projectUsers.forEach(({ idUser }: any) => {
    if (!acc[idUser])
      acc[idUser] = []
    acc[idUser].push({ id, description, engagement: engagement.id })
  })
  return acc
}, {}))
const mapUsers = computed(() => activeUsers.value.map((user) => {
  const { id } = user
  user.projects = projectsPerUser.value[id] || []
  return user
}))

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
      :items="mapUsers"
      :loading="loading"
    />

    <template #out>
      <RequestModal
        v-model="showingRequests"
        :users="pendingUsers"
        @done="loadPage"
      />
    </template>
  </Page>
</template>

<route lang="yaml">
meta:
  permissions: [view_user]
</route>
