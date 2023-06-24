<script setup lang='ts'>
const props = withDefaults(defineProps<{
  icon?: string
  hint?: string
  dark?: boolean
}>(), {
  icon: 'i-carbon-user',
  hint: '',
})
</script>

<template>
  <div
    class="h-7 w-7 p-1.5 rounded-full flex justify-center items-center"
    :class="{
      'bg-black': dark,
      'bg-white border-1 border-gray-6': !dark,
    }"
  >
    <div
      class="w-full h-full"
      :class="{
        [icon]: icon,
        'color-white': dark,
        'color-gray-6': !dark,
      }"
    />
    <QTooltip>
      <div class="whitespace-pre">
        {{ hint.replaceAll('\\n', '\n') }}
      </div>
    </QTooltip>
  </div>
</template>
