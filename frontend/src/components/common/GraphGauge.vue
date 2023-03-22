<script setup lang="ts">
const props = withDefaults(defineProps<{
  values?: { label: string; count: number }[]
  title?: string
  hint?: string
  radius?: number
  strokeWidth?: number
}>(), {
  values: () => [],
  radius: 30,
  strokeWidth: 8,
})

const colors = ['#86BC25', '#005587', '#1abc9c', '#2ecc71', '#3498db', '#9b59b6', '#34495e', '#f1c40f', '#e67e22', '#e74c3c', '#95a5a6', '#ff9ff3']

const mappedValues = computed(() => props.values.reduce((acc: { items: any[]; total: number }, { count, label }) => {
  acc.items.unshift({
    label,
    count: count += acc.total,
  })
  acc.total += count
  return acc
}, { items: [], total: 0 }))

const strokeSize = computed(() => 2 * Math.PI * props.radius)

const total = computed(() => props.values.reduce((acc, { count }) => acc + count, 0))
</script>

<template>
  <div class="bg--base flex flex-col items-stretch gap-3 py-4 px-6 border-1 border-black/12 rounded-.5">
    <div v-if="title" class="flex no-wrap gap-3 items-start font-bold text-xl">
      {{ title }}
      <Hint :value="hint" />
    </div>
    <div class="grid grid-cols-2 flex-1 items-center gap-6">
      <div class="flex justify-center items-center">
        <svg
          :view-box.camel="`0 0 ${2 * radius + strokeWidth} ${2 * radius + strokeWidth}`"
          class="w-80%"
        >
          <circle
            :cx="radius + strokeWidth / 2"
            :cy="radius + strokeWidth / 2"
            :r="radius"
            :stroke-width="strokeWidth"
            stroke="#DFDFDF"
            class="fill-none"
          />
          <circle
            v-for="(item, i) in mappedValues.items"
            :key="item.label"
            :cx="radius + strokeWidth / 2"
            :cy="radius + strokeWidth / 2"
            :r="radius"
            :stroke="i === 0 ? '#DFDFDF' : colors[mappedValues.items.length - i - 1]"
            :stroke-width="strokeWidth"
            class="fill-none origin-center -rotate-90"
            :style="{
              strokeDasharray: strokeSize,
              strokeDashoffset: (1 - (item.count / total)) * strokeSize,
            }"
          />
          <g class="origin-center translate-x-50% translate-y-50%">
            <text y="0" class="font-bold" text-anchor="middle">
              {{ total }}
            </text>
            <text y="10" class="text-[8px]" text-anchor="middle">
              Total
            </text>
          </g>
        </svg>
      </div>
      <div>
        <div v-if="values.length < 1">
          Sem dados disponíveis...
        </div>
        <div
          v-else
          class="grid gap-2 justify-center"
        >
          <div
            v-for="(item, i) in values"
            :key="item.label"
            class="flex items-center gap-2"
          >
            <div
              class="min-w-4 h-4 rounded-full"
              :style="{
                background: i === values.length - 1 ? '#DFDFDF' : colors[i],
              }"
            />
            <div>
              {{ item.label }}
              <span class="bg-gray-2 px-2 py-.5 ml-1 rounded-1 text-xs font-bold">
                {{ item.count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
