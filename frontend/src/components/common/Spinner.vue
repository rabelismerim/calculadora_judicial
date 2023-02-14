<script setup lang="ts">
const props = withDefaults(defineProps<{
  size?: number
  width?: number
}>(), {
  size: 16,
  width: 2,
})
</script>

<template>
  <div
    class="spinner"
    :style="{
      '--size': `${size}px`,
      '--width': `${width}px`,
    }"
  >
    <div /><div /><div /><div />
  </div>
</template>

<style scoped>
.spinner {
  --size: 16px;
  --width: 2px;
  opacity: .8;
  display: inline-block;
  position: relative;
  width: var(--size);
  height: var(--size);
}
.spinner div {
  box-sizing: border-box;
  display: block;
  position: absolute;
  width: var(--size);
  height: var(--size);
  border: var(--width) solid #fff;
  border-radius: 50%;
  animation: spinner 1.2s cubic-bezier(0.5, 0, 0.5, 1) infinite;
  border-color: #fff transparent transparent transparent;
}
.spinner div:nth-child(1) {
  animation-delay: -0.45s;
}
.spinner div:nth-child(2) {
  animation-delay: -0.3s;
}
.spinner div:nth-child(3) {
  animation-delay: -0.15s;
}
@keyframes spinner {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}
</style>
