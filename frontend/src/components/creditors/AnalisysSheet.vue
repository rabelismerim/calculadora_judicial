<script setup lang='ts'>
const props = withDefaults(defineProps<{
  title: string
  subtitle: string
  name: number
  editing: boolean
  loading: boolean
}>(), {
  subtitle: '',
})
const emit = defineEmits(['submit', 'reset', 'edit', 'update:editing', 'update:loading'])

const onEdit = () => emit('update:editing', true)
const onReset = () => {
  emit('update:editing', false)
  emit('reset')
}
const onSubmit = (event: any) => emit('submit', event)
</script>

<template>
  <QStep
    :name="name"
    :title="subtitle"
    icon="o_settings"
    class="bg--primary/10"
  >
    <QForm @submit.prevent="emit('submit', $event)">
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
          <div class="flex gap-2">
            <Btn v-if="editing" label="Cancelar" outlined :disabled="loading" @click="onReset" />
            <Btn v-if="editing" label="Salvar" :loading="loading" loading-label="Salvando..." @click="onSubmit" />
            <Btn v-else label="Editar" @click="onEdit" />
          </div>
        </div>
      </div>
      <slot />
    </QForm>
  </QStep>
</template>
