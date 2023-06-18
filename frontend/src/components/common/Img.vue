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
  errorImage: `${baseUrl}/fallback/image.svg`,
})

const image = ref(null as any)

const onError = () => {
  // image.value.src = props.errorImage
  if (image.value && image.value.src !== props.errorImage)
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
