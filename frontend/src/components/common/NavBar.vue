<script setup lang="ts">
const props = withDefaults(defineProps<{
  showExit?: boolean
}>(), {
  showExit: false,
})

const router = useRouter()
</script>

<template>
  <nav class="flex bg-black h-14 px-8 justify-between items-center sticky top-0 z-100">
    <div class="mr-8 flex items-center gap-6">
      <Img src="/logo/deloitte-small-dark.svg" :height="24" class="sm:hidden" />
      <Img src="/logo/deloitte-dark.svg" :height="24" class="hidden sm:block" />
      <Img src="/logo/app.svg" :height="30" class="hidden sm:block" />
    </div>
    <div class="flex-1">
      <slot />
    </div>
    <div class="flex h-full items-center gap-3">
      <Btn
        v-if="showExit"
        transparent
        color="white"
        grow
        @click="router.push('/')"
      >
        Sair
        <div class="i-carbon-logout" />
      </Btn>
      <Img src="/logo/digital-lab-dark.svg" :height="32" />
    </div>
  </nav>
</template>
