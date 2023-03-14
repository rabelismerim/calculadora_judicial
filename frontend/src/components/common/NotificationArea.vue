<script setup lang="ts">
const { notifications, remove } = $Notification
</script>

<template>
  <div
    class="fixed top-14 left-0 right-0 p-3 pointer-events-none transform transition duration-300 ease-out translate-0 z-1000000"
  >
    <div
      v-auto-animate
      class="w-full max-w-180 mx-auto"
    >
      <div
        v-for="[index, { message, timeout, type, createdAt }] in notifications"
        :key="createdAt"
        :class="{
          'bg--information': type === 'information',
          'bg--success': type === 'success',
          'bg--error': type === 'error',
        }"
        class="grid grid-cols-[32px_1fr_32px] gap-1 text-white pointer-events-auto pt-2 px-1 rounded-.5 border-1 border-black/12 shadow-xl mb-2"
      >
        <div class="flex justify-center items-center text-lg pl-1">
          <div
            :class="{
              'i-carbon-checkmark-outline': type === 'success',
              'i-carbon-warning': type === 'information',
              'i-carbon-misuse-outline': type === 'error',
            }"
          />
        </div>
        <div class="flex text-left items-center px-2">
          {{ message }}
        </div>
        <div
          class="relative right-0 top-0 h-7 aspect-square hover:bg-white/30 rounded-full flex justify-center items-center cursor-pointer transition duration-300 ease-out"
          @click="remove(index)"
        >
          <div class="i-carbon-close text-lg" />
        </div>
        <TimeoutBar
          v-if="timeout"
          :timeout="timeout"
          :type="type"
          class="col-span-3 mb-1"
        />
      </div>
    </div>
  </div>
</template>
