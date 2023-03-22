<script setup lang="ts">
const props = withDefaults(defineProps<{
  title?: string
  hint?: string
}>(), {
})
</script>

<template>
  <div class="bg--base flex flex-col items-stretch gap-3 py-4 px-6 border-1 border-black/12 rounded-.5">
    <div v-if="title" class="flex no-wrap gap-3 items-start font-bold text-xl">
      {{ title }}
      <Hint :value="hint" class="mt-1.25" />
    </div>
    <slot />
  </div>
</template>
