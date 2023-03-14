<script setup lang="ts">
const attrs = useAttrs() as any
const router = useRouter()

let loading = $ref(false)
const filterBy = $ref('')
let project: any = $ref({})

onMounted(async () => {
  loading = true
  try {
    project = await projectService.getProject(attrs.id)
  }
  catch (error) {
    throwError(error)
  }
  finally {
    loading = false
  }
})
</script>

<template>
  <div class="flex flex-1 justify-center">
    <div class="px-8 py-8 max-w-[min(1600px,100vw)] flex-1">
      <button
        class="group mb-8 flex gap-1 items-center uppercase font-semibold hover:text--secondary transition duration-300 ease-in-out"
        @click="router.push({ path: '/projetos' })"
      >
        <div class="i-carbon-chevron-left group-hover:-translate-x-1 transition duration-300 ease-in-out" />
        Voltar
      </button>

      <div class="mb-8 flex justify-between gap-4">
        <h1 class="font-bold text-4xl">
          Projetos
        </h1>
        <Btn
          label="Novo Projeto"
          disabled
        />
      </div>

      <div>
        {{ project }}
      </div>
    </div>
  </div>
</template>

<route lang="yaml">
meta:
  authentication: true
</route>
