<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: boolean
  user?: any
  loading?: boolean
}>(), {
  modelValue: false,
})
const emit = defineEmits(['update:modelValue', 'success'])
const router = useRouter()

const goTo = (project: any) => {
  router.push({ path: `/projeto/${project.id}` })
}
</script>

<template>
  <Modal
    :model-value="modelValue"
    :title="`Projetos de ${user.fullName}`"
    hint="Existe um cadastro prévio para o cadastro de projetos na ferramenta."
    :loading="loading"
    @update:model-value="(value: boolean) => emit('update:modelValue', value)"
  >
    <div class="flex gap-1 pb-8 px-8">
      <div
        v-for="project in user.projects as any[]"
        :key="project.id"
        class="rounded-full px-3 py-1 border-1 border--black/10 bg-gray/10 whitespace-nowrap cursor-pointer hover:bg--primary/20"
        @click="goTo(project)"
      >
        {{ project.description }}
      </div>
    </div>
  </Modal>
</template>
