<script setup lang="ts">
const props = withDefaults(defineProps<{
  showExit?: boolean
}>(), {
})

const router = useRouter()
const logout = () => {
  $user.logout()
  router.push({ path: '/' })
}
const { user } = $user
</script>

<template>
  <nav class="flex bg-black h-14 pl-3 md:pl-8 md:pr-8 justify-between items-center sticky top-0 z-100">
    <div class="md:mr-8 flex items-center">
      <Img :src="`${baseUrl}/logo/deloitte-small-dark.svg`" :height="24" class="sm:hidden" />
      <Img :src="`${baseUrl}/logo/deloitte-dark.svg`" :height="24" class="hidden sm:block" />
      <Img :src="`${baseUrl}/logo/app.svg`" :height="30" class="hidden md:block" />
    </div>
    <div class="flex no-wrap flex-1 h-full overflow-x-auto overflow-y-hidden hide-scrollbar">
      <slot />
    </div>
    <div class="flex h-full items-center gap-3">
      <Btn
        v-if="showExit"
        transparent
        grow
        color="white"
        :label="user.name || 'sair'"
        icon="i-carbon-logout"
        tooltip="Sair do Sitema!"
        @click="logout"
      >
        <template #before>
          <div v-if="!user.picture" class="mr-2 h-8 w-8 bg--secondary text-sm flex justify-center items-center rounded-full">
            {{ getInitials(user.name) }}
          </div>
          <div v-else class="h-8 w-8 rounded-full overflow-hidden bg-red">
            <Img
              :src="`data:image/jpeg;base64,${user.picture}`"
              :error-image="`${baseUrl}/fallback/user.svg`"
              class="h-8 w-8 object-cover"
            />
          </div>
        </template>
      </Btn>
      <Img
        :src="`${baseUrl}/logo/digital-lab-dark.svg`"
        :height="32"
        class="hidden md:block"
      />
    </div>
  </nav>
</template>
