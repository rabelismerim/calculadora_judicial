<script setup lang='ts'>
const props = withDefaults(defineProps<{
  calculation: any
  colors: any
}>(), {

})
const emit = defineEmits(['reloadClick'])
</script>

<template>
  <Header>
    <template #bottom>
      <span v-if="calculation?.step" class="self-center mr-3 font-bold text-lg">Status do Cálculo</span>
      <StatusTag
        v-if="calculation?.step"
        :label="calculation?.stepDisplay "
        :color="colors[calculation?.step]"
      />
    </template>
    <template #title>
      <div class="flex gap-2 font-bold text-3xl">
        <div>Cálculo #{{ calculation?.number || '' }}</div>
        -
        <div>{{ calculation?.creditor?.entity?.name || '' }}</div>
        <ReloadBtn
          hint="Recarregar a Lista de Créditos"
          @click="emit('reloadClick')"
        />
      </div>
    </template>
    <slot />
  </Header>
</template>
