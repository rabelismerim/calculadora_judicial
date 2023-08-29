<script>
export default {
  name: 'Test',
  data() {
    return {
      responseData: null,
      error: null,
    }
  },
  methods:
    {
      async fetchData() {
        try {
          const projectId = 'db559f9b-e678-4066-9f7d-e9404345814f'
          const response = await validationService.getDetailId(projectId)
          this.responseData = response
          this.error = null
        }
        catch (error) {
          this.error = `Erro ao buscar os dados:${error.message}`
          this.responseData = null
        }
      },
    },
}
</script>

<template>
  <h1>TESTE VALIDATION ENDPOINTS</h1>
  <br>
  <div>
    <Btn @click="fetchData" />
    <div v-if="responseData">
      <pre>{{ responseData }}</pre>
    </div>

    <div v-if="error">
      <p>{{ error }}</p>
    </div>
  </div>
</template>

<!-- <div v-if="responseData">
  <p>ID: {{ responseData.id }}</p>
  <p>created_at_min: {{ responseData.createAtMin }}</p>
  <p>created_at_max: {{ responseData.createAtMax }}</p>
  <p>update_at_min: {{ responseData.updateAtMin }}</p>
  <p>update_at__max: {{ responseData.updateAtMax }}</p>
</div>
<div v-if="error">
  <p>Error: {{ error }}</p> -->
