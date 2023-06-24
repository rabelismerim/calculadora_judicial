<script setup lang="ts">
import links from '@/assets/footer-links.json'

const props = withDefaults(defineProps<{
  showLinks?: boolean
}>(), {
})

const appVersion = APP_VERSION || '0.0.0'
</script>

<template>
  <footer class="z-100">
    <div v-if="showLinks" class="flex flex-col sm:flex-row justify-center p-2 bg-[#F5F5F4] border-t-1 border-[#D0D0CE]">
      <a
        v-for="({ title, url }, index) in links as any[]" :key="title" :href="url"
        :class="{ 'sm:border-l-1 border-[#D0D0CE]': index > 0 }" class="px-2"
      >
        {{ title }}
      </a>
    </div>
    <div class="flex items-center justify-center sm:justify-between bg-black h-10 px-10 text-white overflow-hidden">
      <div class="inline sm:block">
        © 2023 Para mais informações contate a Deloitte Global
      </div>
      <span class="ml-4 whitespace-pre">Versão: {{ appVersion }}</span>
    </div>
  </footer>
</template>
