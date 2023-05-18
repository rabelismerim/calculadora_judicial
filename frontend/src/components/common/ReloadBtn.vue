<script setup lang="ts">
const props = withDefaults(defineProps<{
  hint?: string
}>(), {

})
const emit = defineEmits(['click'])
</script>

<template>
  <button
    class="h-8 w-8 hover:bg-gray/30 rounded-full flex justify-center items-center tween"
    @click="emit('click')"
  >
    <div class="i-carbon-restart h-5 w-5" />
    <QTooltip v-if="hint">
      {{ hint }}
    </QTooltip>
  </button>
</template>
