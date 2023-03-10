<script setup lang="ts">
const props = withDefaults(defineProps<{
  values?: { label: string; count: number }[]
  title?: string
  hint?: string
}>(), {
  values: () => [],
})

const biggestValue = computed(() => [...props.values]?.sort(({ count: a }, { count: b }) => a < b ? 1 : -1)?.at(0)?.count || 0)
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
        class="max-h-40 overflow-y-auto"
      >
        <div
          v-for="{ label, count } in values"
          :key="label"
          class="grid grid-cols-[1fr_2fr] items-center"
        >
          <div>{{ label }}</div>
          <div class="relative h-4 bg-gray-3 rounded-full overflow-hidden">
            <div
              class="h-full bg--secondary rounded-full"
              :style="{
                width: `${count / biggestValue * 100}%`,
              }"
            />
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
