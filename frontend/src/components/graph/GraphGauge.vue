<script setup lang="ts">
import { rangeBetween } from '../../composables/utils'

const props = withDefaults(defineProps<{
  values?: { label: string; count: number; color?: string }[]
  title?: string
  emptyLabel?: string
  hint?: string
  radius?: number
  strokeWidth?: number
  contentClass?: string
}>(), {
  values: () => [],
  radius: 30,
  strokeWidth: 8,
  contentClass: 'grid-cols-2',
  emptyLabel: 'Sem dados disponíveis...',
})

const colors = computed(() => [...rangeBetween(44, 10, props.values.length - 1), 0]
  .map(lighting => `hsl(81, 68%, ${lighting}%)`))

const mappedValues = computed(() => props.values.reduce((acc: { items: any[]; total: number }, { count, label, color }) => {
  acc.items.push({
    label,
    color,
    count,
    start: acc.total,
  })
  acc.total += count
  return acc
}, { items: [], total: 0 }).items)

const strokeSize = computed(() => 2 * Math.PI * props.radius)

const total = computed(() => props.values.reduce((acc, { count }) => acc + count, 0))
const isAllNull = computed(() => props.values.every(({ count }: any) => count === 0))
</script>

<template>
  <div class="bg--base flex flex-col items-stretch gap-3 py-4 px-6 border-1 border-black/12 rounded-.5">
    <div v-if="title" class="flex no-wrap gap-3 items-start font-bold text-xl">
      {{ title }}
      <Hint :value="hint" class="mt-1.25" />
    </div>
    <div
      class="grid flex-1 items-center gap-6"
      :class="contentClass"
    >
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
          <g v-if="!isAllNull">
            <circle
              v-for="(item, i) in mappedValues"
              :key="item.label"
              :cx="radius + strokeWidth / 2"
              :cy="radius + strokeWidth / 2"
              :r="radius"
              :stroke="item.color ? item.color : colors[i]"
              :stroke-width="strokeWidth"
              class="fill-none origin-center -rotate-90"
              :style="{
                strokeDasharray: strokeSize,
                strokeDashoffset: (1 - (item.count / total)) * strokeSize,
                transform: `rotate(${(360 / total) * item.start - 90}deg)`,
              }"
            />
          </g>
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
          {{ emptyLabel }}
        </div>
        <div
          v-else
          class="grid gap-2 justify-center"
        >
          <div
            v-for="(item, i) in values"
            :key="item.label"
            class="flex items-center gap-2 no-wrap"
          >
            <div
              class="min-w-4 h-4 rounded-full"
              :style="{
                background: item.color ? item.color : colors[i],
              }"
            />
            <div class="whitespace-pre text-[12px]">
              {{ item.label }}
              <span class="bg-gray-2 px-1 py-.5 ml-1 rounded-1 font-bold text-[11px]">
                {{ item.count }}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>
