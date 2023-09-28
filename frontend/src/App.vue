<script setup lang="ts">
const { user } = $user

onMounted(() => {
  const preventEvent = (evt: Event) => evt.preventDefault()
  window.addEventListener('dragover', preventEvent, false)
  window.addEventListener('drop', preventEvent, false)
})
</script>

<template>
  <RouterView />
  <NotificationArea />
</template>
