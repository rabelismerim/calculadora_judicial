<script setup lang="ts">
const props = withDefaults(defineProps<{
  status?: string
}>(), {

})

const steps = [
  {
    label: 'à Calcular',
    background: '#AAAAAA',
    color: '#000',
    status: 'S',
  },
  {
    label: 'à Revisar',
    background: '#C4D600',
    color: '#000',
    status: 'C',
  },
  {
    label: 'à Aprovar',
    background: '#86BC25',
    color: '#FFF',
    status: 'E',
  },
  {
    label: 'à Aprovar Especialmente',
    background: '#43B02A',
    color: '#FFF',
    status: 'B',
    hint: 'opcional',
  },
  {
    label: 'Finalizado',
    background: '#007CB0',
    color: '#FFF',
    status: 'A',
  },
]
</script>

<template>
  <div class="flex gap-1 font-bold">
    <div
      v-for="(step, index) in steps" :key="step.label"
      class="flex no-wrap"
      :class="{
        '-mr-4': index < steps.length - 1,
      }"
    >
      <div
        v-if="index !== 0"
        class="inline-block h-full border-solid border-18 border-r-0 border-x-transparent"
        :style="{
          borderTopColor: step.background,
          borderBottomColor: step.background,
        }"
      />
      <div
        class="relative py-2 text-sm"
        :class="{
          'pl-3 rounded-l': index === 0,
          'pl-1.5': index > 0,
          'pr-3 rounded-r': index === steps.length - 1,
        }"
        :style="{
          color: step.color,
          backgroundColor: step.background,
        }"
      >
        <div class="whitespace-nowrap overflow-hidden text-ellipsis">
          {{ step.label }}
        </div>
        <div class="flex gap-1 -translate-y-55% text-white font-medium text-xs absolute top-0">
          <div v-if="step.hint" class="bg-slate-2 text-black px-2 py-.2 rounded-full">
            {{ step.hint }}
          </div>
          <div v-if="status && step.status === status" class="bg-gray-9 px-2 py-.2 rounded-full">
            atual
          </div>
        </div>
      </div>
      <div
        v-if="index !== steps.length - 1"
        class="relative inline-block h-full border-solid border-18 border-r-0 border-y-transparent"
        :style="{
          borderLeftColor: step.background,
        }"
      />
    </div>
  </div>
</template>
