<script setup lang="ts">
const router = useRouter()
const route = useRoute()
const getColor = (path: string) => route.path === path ? 'secondary' : 'white'
const { hasPermissions } = $user

let accessRequestsCount = $ref(0)
onMounted(async () => {
  try {
    if (hasPermissions(['view_user'])) {
      const users = await usersService.getUsers()
      accessRequestsCount = users.filter(({ status }: any) => status.toLowerCase() === 'p').length
    }
  }
  catch (error) {
    printError('ERROR ON LOAD DEFAULT LAYOUT OPTIONS:', error)
  }
})

interface Link {
  label: string
  path: string
  disabled?: boolean
  permissions?: string[]
  notification?: number
}
const paths: Link[] = $ref([
  {
    label: 'Home',
    path: '/',
  },
  {
    label: 'Projetos',
    path: '/projetos',
  },
  {
    label: 'Time',
    path: '/time',
    notification: computed(() => accessRequestsCount),
    permissions: ['view_user'],
  },
])
const filteredPaths = computed(() => paths.filter(({ permissions }: any) => hasPermissions(permissions)))
</script>

<template>
  <NavBar show-exit>
    <Btn
      v-for="({ label, path, notification, disabled }, index) in filteredPaths"
      :key="index"
      :label="label"
      grow
      transparent
      :disabled="disabled"
      :color="getColor(path)"
      :class="{ 'pr-6': notification }"
      @click="router.push({ path })"
    >
      <div v-if="notification" class="relative inline-block mb-3">
        <span class="bg--error text-white absolute top-0 animate-bounce text-xs rounded-full py-.3 px-1.5">
          {{ notification }}
        </span>
      </div>
    </Btn>
  </NavBar>
  <div class="flex flex-1 flex-col">
    <RouterView />
  </div>
  <FooterBar />
</template>
