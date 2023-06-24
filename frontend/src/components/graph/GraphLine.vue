<script setup lang="ts">
const props = withDefaults(defineProps<{
  values?: { label: string; count: number }[]
  title?: string
  hint?: string
  padding?: number
  gap?: number
  border?: number
}>(), {
  values: () => [],
  padding: 16,
  gap: 8,
  border: 1,
})

const size = $ref({ width: 0, height: 0 })
const onResize = ({ width, height }: any) => {
  size.width = width
  size.height = height
}
const w = computed(() => size.width + 2 * props.padding + 2 * props.border)
const h = computed(() => size.height + 2 * props.padding + 2 * props.border + 15)
const count = computed(() => props.values.length)

const axis = computed(() => ({
  top: 1,
  left: 1,
  width: size.width - 2,
  height: size.height - 17,
}))
const maxValue = computed(() => props.values.reduce((acc, [, value]: any) => value > acc ? value : acc, 0))
const getBar = (value: number, index: number) => {
  const h = value / maxValue.value * (size.height - props.padding - 22)
  return {
    y: size.height - h - 32,
    x: size.width / (count.value - 1) * index,
  }
}
const bars = computed(() => props.values
  .map(([label, value]: any, index) => ({
    label,
    value,
    ...getBar(value, index),
  })))

const path = computed(() => {
  const [{ x, y }, ...rest] = bars.value
  return `M${x},${y} L${rest.map(({ x, y }) => `${x},${y}`).join(' ')}`
})
const closePath = computed(() => `${path.value} L${axis.value.width},${axis.value.height - 16} ${axis.value.left},${axis.value.height - 16} Z`)
</script>

<template>
  <div class="relative bg--base flex flex-col items-stretch gap-3 py-4 px-6 border-1 border-black/12 rounded-.5 min-h-57">
    <div v-if="title" class="flex no-wrap gap-3 items-start font-bold text-xl">
      {{ title }}
      <Hint :value="hint" class="mt-1.25" />
    </div>
    <div v-resize:0="onResize" class="flex-1 items-center">
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
        <svg xmlns="http://www.w3.org/2000/svg" version="1.1" :view-box.camel="`0 0 ${size.width} ${size.height}`">
          <linearGradient id="grad" x1="0%" y1="0%" x2="0%" y2="100%">
            <stop offset="0%" class="stop--secondary/50" />
            <stop offset="100%" class="stop--secondary/0" />
          </linearGradient>
          <g :style="{ transform: `translateY(${padding}px)` }">
            <path :d="closePath" fill="url(#grad)" />
            <path :d="path" class="fill-none stroke-4 stroke--secondary" />
            <g v-for="({ label, value, x, y }, i) in bars" :key="i">
              <circle :cx="x" :cy="y" r="4" rx="2" class="fill--secondary/60 stroke--secondary stroke-1" />
              <text :x="x" :y="size.height - 16">{{ label }}</text>
              <text v-if="value !== 0" :x="x" :y="y - 10">{{ value }}</text>
            </g>
          </g>
          <path stroke="#64748b" fill="none" stroke-width="2" :d="`M${axis.left} ${axis.top} v${axis.height}h${axis.width}`" />
        </svg>
      </div>
    </div>
  </div>
</template>
