<script setup lang='ts'>
const props = withDefaults(defineProps<{
  title?: string
  tag?: string | number
}>(), {
  title: '',
})
</script>

<template>
  <div class="mb-4 flex flex-col gap-2">
    <div v-if="$slots.top" class="flex">
      <slot name="top" />
    </div>
    <div class="flex justify-between gap-4">
      <div class="flex no-wrap gap-2 items-center">
        <div v-if="$slots.title">
          <slot name="title" />
        </div>
        <h2 v-else class="font-bold text-4xl">
          {{ title }}
        </h2>
        <div v-if="tag" class="px-2.5 bg--content/50 text--base rounded-full font-bold text-5 border-1 border--content/12">
          {{ tag }}
        </div>
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
