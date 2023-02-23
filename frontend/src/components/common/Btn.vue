<script setup lang="ts">
const props = withDefaults(defineProps<{
  label?: string
  loadingLabel?: string
  icon?: string
  align?: string
  loading?: boolean
  color?: string
  transparent?: boolean
  grow?: boolean
  disabled?: boolean
  outlined?: boolean
}>(), {
  label: 'Clique aqui',
  loadingLabel: 'Carregando...',
  color: 'primary',
  align: 'center',
})

const emit = defineEmits(['click'])

const shine = $ref({
  show: false,
  x: 5,
  y: 0,
})

const button = ref(null) as unknown as { value: HTMLElement }
const onMouseMove = (event: MouseEvent) => {
  const { x: positionX = 0, y: positionY = 0, target } = event
  if (target !== button.value)
    return

  const { x = 0, y = 0 } = button?.value?.getBoundingClientRect() || {}
  shine.x = positionX - x
  shine.y = positionY - y
}
</script>

<template>
  <button
    ref="button"
    v-auto-animate
    :disabled="disabled"
    class="relative overflow-hidden text-[1.05rem] min-h-10 font-semibold px-8 py-2 flex gap-4 no-wrap items-center transition duration-300 ease-in-out"
    :class="{
      'text--color border-1 border--color rounded-.5': outlined,
      'hover:bg--base/10 text--color rounded-.5': transparent,
      'bg--color text-white border-1 border-black/12 rounded-.5': !transparent && !outlined,
      'h-full rounded-0': grow,
      'active:scale-110': !grow && !disabled,
    }"
    :style="{
      'justify-content': align,
      '--color': `var(--${color})`,
    }"
    @click="emit('click')"
    @mouseenter="shine.show = true"
    @mouseleave="shine.show = false"
    @mousemove="onMouseMove"
  >
    <div v-if="loading" class="pointer-events-none">
      {{ loadingLabel }}
    </div>
    <div v-else class="pointer-events-none">
      {{ label }}
    </div>
    <Spinner v-if="loading" :color="!transparent && !outlined ? 'white' : color" class="pointer-events-none" />
    <div v-if="icon" :class="icon" class="transition duration-300 ease-in-out pointer-events-none" />
    <div
      class="h-300% aspect-square rounded-full absolute -translate-x-50% -translate-y-50% transition-opacity duration-300 ease-in-out pointer-events-none"
      :class="{
        'mix-blend-color-dodge': !transparent && !outlined,
      }"
      :style="{
        backgroundImage: `radial-gradient(${transparent || outlined ? 'hsl(var(--color),.2)' : '#ddd5'} 10%,#0000 70%)`,
        opacity: shine.show ? 1 : 0,
        left: `${shine.x}px`,
        top: `${shine.y}px`,
      }"
    />
  </button>
</template>
