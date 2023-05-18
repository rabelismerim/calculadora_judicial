<script setup lang='ts'>
const props = withDefaults(defineProps<{
  title?: string
}>(), {
  title: '',
})
</script>

<template>
  <div class="flex justify-between mb-8 gap-4">
    <div class="flex no-wrap gap-2 items-center">
      <h2 class="font-bold text-3xl">
        {{ title }}
      </h2>
      <slot name="side" />
    </div>
    <div class="flex items-center gap-2">
      <slot />
    </div>
  </div>
</template>
