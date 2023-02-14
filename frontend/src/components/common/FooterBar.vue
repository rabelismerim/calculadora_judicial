<script setup lang="ts">
import links from '@/assets/footer-links.json'
</script>

<template>
  <footer class="z-100">
    <div class="flex flex-col sm:flex-row justify-center p-3 bg-[#F5F5F4] border-t-1 border-[#D0D0CE]">
      <a
        v-for="({ title, url }, index) in links"
        :key="title"
        :href="url"
        :class="{ 'sm:border-l-1 border-[#D0D0CE]': index > 0 }"
        class="px-2"
      >
        {{ title }}
      </a>
    </div>
    <div class="flex bg-black h-20 px-10 text-white justify-between items-center">
      <p>© 2023 Para mais informações contate a Deloitte Global</p>
    </div>
  </footer>
</template>
