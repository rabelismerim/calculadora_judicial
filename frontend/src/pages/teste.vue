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
          const objectId = '3f51742d-c6b0-4637-9627-fa041c9eafa5'
          const path = 'project'
          const name = 'create_creditors_claim'
          const response = await uploadService.putErrorDetail()
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
  <h1>TESTE UPLOAD ENDPOINTS</h1>
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
