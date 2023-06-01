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
</script>

<template>
  <component
    :is="tag"
    ref="button"
    :disabled="disabled ? disabled : undefined"
    class="group relative overflow-hidden text-[1.05rem] min-h-10 font-semibold px-4 py-2 flex gap-[.5em] no-wrap items-center tween cursor-pointer"
    :class="{
      'text--color border-1 border--color rounded-.5': outlined,
      'hover:bg--color/10 text--color rounded-.5': transparent,
      'bg--color text-white border-1 border-black/12 rounded-.5': !transparent && !outlined,
      'h-full rounded-0 min-w-fit': grow,
      'active:scale-110': !grow && !disabled && !transparent,
    }"
    :style="{
      'justify-content': align,
      '--color': `var(--${color})`,
    }"
    tabindex="0"
    @keyup.space="emit('press')"
    @click="emit('click', $event)"
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
    <slot v-if="$slots.default" />
    <div
      class="opacity-0 group-hover:opacity-15 inset-0 absolute tween"
      :class="{
        'mix-blend-color-burn bg-gray-6': !transparent && !outlined,
        'mix-blend-screen bg-current-color': transparent || outlined,
      }"
    />
    <QTooltip v-if="tooltip">
      {{ tooltip }}
    </QTooltip>
  </component>
</template>
