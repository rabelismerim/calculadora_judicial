<script setup lang="ts">
const count = ref(0)
</script>

<template>
  <div class="card">
    <button
      type="button"
      class="px-4 py-2"
      @click="count++"
    >
      count is {{ count }}
    </button>
    <p class="mt-3">
      Edit
      <code>components/HelloWorld.vue</code> to test HMR
    </p>
  </div>
</template>

<style scoped>
.read-the-docs {
  color: #888;
}
</style>
