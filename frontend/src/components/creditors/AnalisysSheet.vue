<script setup lang='ts'>
const props = withDefaults(defineProps<{
  title: string
  subtitle: string
  name: number
}>(), {
  subtitle: '',
})
</script>

<template>
  <QStep
    :name="name"
    :title="subtitle"
    icon="o_settings"
    class="bg--primary/10"
  >
    <QForm @submit.prevent>
      <div class="flex">
        <div>
          <div class="font-bold text-lg">
            {{ title }}
          </div>
          <div class="color--primary uppercase font-bold">
            {{ name }} - {{ subtitle }}
          </div>
        </div>
        <div class="flex flex-1 justify-end">
          <slot name="side" />
        </div>
      </div>
      <slot />
    </QForm>
  </QStep>
</template>
