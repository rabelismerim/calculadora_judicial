<script setup lang="ts">
const props = withDefaults(defineProps<{
  label: string
  color?: string
}>(),
{
  color: '#007db3',
})
</script>

<template>
  <div
    class="py-1 pl-3 rounded-full flex no-wrap items-center"
    :style="{
      background: `${color}20`,
    }"
  >
    <div class="flex-1">
      {{ label }}
    </div>
    <div
      class="h-4 w-4 rounded-full mr-2 ml-1.5"
      :style="{
        background: color,
      }"
    />
  </div>
</template>
