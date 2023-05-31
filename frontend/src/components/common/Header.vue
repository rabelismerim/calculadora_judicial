<script setup lang='ts'>
const props = withDefaults(defineProps<{
  title?: string
}>(), {
  title: '',
})
</script>

<template>
  <div class="mb-8 flex flex-col gap-2">
    <div v-if="$slots.top" class="flex">
      <slot name="top" />
    </div>
    <div class="flex justify-between gap-4">
      <div class="flex no-wrap gap-2 items-center">
        <h2 class="font-bold text-4xl">
          {{ title }}
        </h2>
        <slot name="side" />
      </div>
      <div class="flex items-center gap-2">
        <slot />
      </div>
    </div>
    <div v-if="$slots.bottom" class="flex">
      <slot name="bottom" />
    </div>
  </div>
</template>
