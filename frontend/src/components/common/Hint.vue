<script setup lang="ts">
const props = withDefaults(defineProps<{
  value?: String
}>(), {
})
</script>

<template>
  <div v-if="value" class="cursor-help text-base">
    <div class="i-carbon-help-filled color-black/30 hover:color--primary tween" />
    <QTooltip>
      <div class="whitespace-pre">
        {{ value.replaceAll('\\n', '\n') }}
      </div>
    </QTooltip>
  </div>
</template>
