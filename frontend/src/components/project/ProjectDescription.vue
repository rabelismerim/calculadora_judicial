<script setup lang='ts'>
const props = withDefaults(defineProps<{
  project?: any
}>(), {
  project: () => ({}),
})
</script>

<template>
  <ProjectDetailCell label="Engagement">
    <div v-for="(engagement, index) in project?.engagement?.numbers" :key="index">
      {{ engagement }}
    </div>
  </ProjectDetailCell>

  <ProjectDetailCell label="Sócio Jurídico">
    {{ project?.legalPartner?.fullName || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Sócio Financeiro">
    {{ project?.financialPartner?.fullName || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Gerente Jurídico">
    {{ project?.legalManager?.fullName || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Gerente Financeiro">
    {{ project?.financialManager?.fullName || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Gerente de Cálculo">
    {{ project?.calculationManager?.fullName || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Recuperandas">
    <div
      v-for="recovering in project?.recoverings as any[]"
      :key="recovering.id"
      class="mb-2"
    >
      <div class="font-bold">
        {{ recovering.entity.name }}
      </div>
      <div>{{ formatLegalNumber(recovering.entity.legalNumber) }}</div>
    </div>
  </ProjectDetailCell>

  <ProjectDetailCell label="Data de Pedido de Recuperação">
    {{ formatDateFromBackend(project?.projectStart) || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Número do Processo Principal">
    {{ project?.processNumber || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Juiz">
    {{ toProperName(project?.judge?.description || '') || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Advogado">
    {{ toProperName(project?.lawyer?.description || '') || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Comarca">
    {{ project?.region?.description || '-' }}
  </ProjectDetailCell>

  <ProjectDetailCell label="Vara">
    {{ project?.court?.description || '-' }}
  </ProjectDetailCell>
</template>
