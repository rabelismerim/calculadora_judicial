<script setup lang="ts">
const props = withDefaults(defineProps<{
  color?: string
  transparent?: boolean
  grow?: boolean
}>(), {
  color: 'primary',
  transparent: false,
  grow: false,
})

const emit = defineEmits(['click'])
</script>

<template>
  <button
    class="flex no-wrap items-center h-10 font-semibold gap-4 px-8 py-2 roudend-0"
    :class="{
      'bg--color text-white': !transparent,
      'hover:bg-white/20 text--color': transparent,
      'h-full': grow,
    }"
    :style="{
      '--color': `var(--${color})`,
    }"
    @click="emit('click')"
  >
    <slot />
  </button>
</template>
