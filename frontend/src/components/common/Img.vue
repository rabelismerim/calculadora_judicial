<script setup lang="ts">
const props = withDefaults(defineProps<{
  src?: string
  alt?: string
  width?: number
  height?: number
  errorImage?: string
}>(), {
  src: '',
  alt: '',
  errorImage: '/fallback/image.svg',
})

const image = ref(null) as unknown as { value: HTMLImageElement }

const onError = () => {
  image.value.src = props.errorImage
}
</script>

<template>
  <img
    ref="image"
    :src="src"
    :style="{
      width: `${width}px`,
      height: `${height}px`,
    }"
    @error="onError"
  >
</template>
