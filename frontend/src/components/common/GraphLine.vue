<script setup lang="ts">
const props = withDefaults(defineProps<{
  values?: { label: string; count: number }[]
  title?: string
  hint?: string
}>(), {
  values: () => [],
})
</script>

<template>
  <div class="bg--base flex flex-col items-stretch gap-3 py-4 px-6 border-1 border-black/12 rounded-.5">
    <div v-if="title" class="flex no-wrap gap-3 items-start font-bold text-xl">
      {{ title }}
      <Hint :value="hint" />
    </div>
    <div class="flex-1 items-center">
      <div
        v-if="values.length < 1"
        class="flex items-center justify-center h-full"
      >
        Sem dados disponíveis...
      </div>
      <div
        v-else
        class=""
      >
        teste...
      </div>
    </div>
  </div>
</template>
