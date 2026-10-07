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
    <div class="flex items-center">
      <span class="font-bold text-white text-sm sm:text-lg whitespace-nowrap">Calculadora Judicial</span>
    </div>
    <div class="flex no-wrap flex-1 h-full overflow-x-auto overflow-y-hidden hide-scrollbar">
      <slot />
    </div>
    <div class="flex h-full items-center gap-5">
      <Btn
        v-if="showExit"
        transparent
        grow
        color="white"
        icon="i-carbon-logout"
        tooltip="Sair do Sitema!"
        @click="logout"
      >
        <template #before>
          <UserPicture
            :model-value="user"
            class="h-8 w-8 rounded-full"
            initials-class="text-sm"
          />
        </template>
        <template #label>
          <div class="hidden sm:block">
            {{ user.fullName || 'sair' }}
          </div>
        </template>
      </Btn>
      <Img :src="`${baseUrl}/logo/calculator.svg`" :height="30" alt="Calculadora" class="hidden md:block" />
    </div>
  </nav>
</template>
