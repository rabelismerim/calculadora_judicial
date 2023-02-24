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
</script>

<template>
  <nav class="flex bg-black h-14 px-8 justify-between items-center sticky top-0 z-100">
    <div class="mr-8 flex items-center gap-6">
      <Img :src="`${baseUrl}/logo/deloitte-small-dark.svg`" :height="24" class="sm:hidden" />
      <Img :src="`${baseUrl}/logo/deloitte-dark.svg`" :height="24" class="hidden sm:block" />
      <Img :src="`${baseUrl}/logo/app.svg`" :height="30" class="hidden sm:block" />
    </div>
    <div class="flex no-wrap flex-1 h-full overflow-x-auto overflow-y-hidden">
      <slot />
    </div>
    <div class="flex h-full items-center gap-3">
      <Btn
        v-if="showExit"
        transparent
        grow
        color="white"
        label="Sair"
        icon="i-carbon-logout"
        @click="logout"
      />
      <Img :src="`${baseUrl}/logo/digital-lab-dark.svg`" :height="32" />
    </div>
  </nav>
</template>
