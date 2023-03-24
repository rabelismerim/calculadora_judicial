<script setup lang="ts">
const props = withDefaults(defineProps<{
  label?: string
  loadingLabel?: string
  icon?: string
  align?: string
  loading?: boolean
  color?: string
  transparent?: boolean
  tooltip?: string
  grow?: boolean
  disabled?: boolean
  outlined?: boolean
  tag?: string
}>(), {
  label: 'Clique aqui',
  loadingLabel: 'Carregando...',
  color: 'primary',
  align: 'center',
  tag: 'button',
})

const emit = defineEmits(['click', 'press'])

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
  <component
    :is="tag"
    ref="button"
    :disabled="disabled ? disabled : undefined"
    class="relative overflow-hidden text-[1.05rem] min-h-10 font-semibold px-4 py-2 flex gap-4 no-wrap items-center tween cursor-pointer"
    :class="{
      'text--color border-1 border--color rounded': outlined,
      'hover:bg--base/10 text--color rounded': transparent,
      'bg--color text-white border-1 border-black/12 rounded': !transparent && !outlined,
      'h-full rounded-0 min-w-fit': grow,
      'active:scale-110': !grow && !disabled,
    }"
    :style="{
      'justify-content': align,
      '--color': `var(--${color})`,
    }"
    tabindex="0"
    @keyup.space="emit('press')"
    @click="emit('click')"
    @mouseenter="shine.show = true"
    @mouseleave="shine.show = false"
    @mousemove="onMouseMove"
  >
    <div v-show="loading" class="flex items-center nowrap gap-4 pointer-events-none whitespace-nowrap">
      {{ loadingLabel }}
      <Spinner
        :color="!transparent && !outlined ? 'white' : color"
        class="pointer-events-none tween"
        :class="loading ? 'opacity-100 scale-100' : 'opacity-0 scale-0'"
      />
    </div>
    <div v-show="!loading" class="pointer-events-none flex items-center gap-2 no-wrap">
      <slot name="before" />
      <span class="whitespace-nowrap">{{ label }}</span>
      <slot name="after" />
    </div>
    <div v-show="icon" :class="icon" class="tween pointer-events-none" />
    <div
      class="h-300% aspect-square rounded-full absolute -translate-x-50% -translate-y-50% transition-opacity duration-300 ease-in-out pointer-events-none"
      :class="{
        'mix-blend-color-dodge': !transparent && !outlined,
      }"
      :style="{
        backgroundImage: `radial-gradient(${transparent || outlined ? 'hsl(var(--color),.2)' : '#ddd5'} 10%,#0000 70%)`,
        opacity: shine.show && !disabled ? 1 : 0,
        left: `${shine.x}px`,
        top: `${shine.y}px`,
      }"
    />
    <QTooltip v-if="tooltip">
      {{ tooltip }}
    </QTooltip>
  </component>
</template>
