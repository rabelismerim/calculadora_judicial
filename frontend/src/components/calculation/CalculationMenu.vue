<script setup lang='ts'>
const props = withDefaults(defineProps<{
  modelValue: string
  project: any
  calculation: any
  recovering: any
  creditor: any
}>(), {
})
const emit = defineEmits(['update:modelValue'])
</script>

<template>
  <QTabPanels
    :model-value="modelValue"
    animated class="calculation-details"
    @update:model-value="value => emit('update:modelValue', value)"
  >
    <QTabPanel name="project" class="px-0">
      <ProjectDescription :project="project" />
    </QTabPanel>
    <QTabPanel name="analysis" class="px-0">
      <ProjectDetailCell label="Id">
        {{ `#${calculation?.number}` || '-' }}
      </ProjectDetailCell>
      <ProjectDetailCell label="Incidente">
        {{ calculation?.incident?.number || '-' }}
      </ProjectDetailCell>
      <ProjectDetailCell label="Recuperanda">
        {{ recovering?.entity?.name || '-' }}
      </ProjectDetailCell>
      <ProjectDetailCell label="Recuperanda - CNPJ">
        {{ formatLegalNumber(recovering?.entity?.legalNumber) || '-' }}
      </ProjectDetailCell>
      <ProjectDetailCell label="Credor">
        {{ creditor?.entity?.name || '-' }}
      </ProjectDetailCell>
      <ProjectDetailCell :label="`Credor - ${creditor?.entity?.legalNumber?.length === 11 ? 'CPF' : 'CNPJ'}`">
        {{ formatLegalNumber(creditor?.entity?.legalNumber) || '-' }}
      </ProjectDetailCell>
      <ProjectDetailCell label="Classes">
        <div
          v-for="classe in calculation?.classes as any[]"
          :key="classe.id"
        >
          {{ classe.classeDisplay }}: {{ classe.totalValue }}%
        </div>
      </ProjectDetailCell>

      <div class="font-bold color--primary uppercase">
        Critério
      </div>
      <ProjectDetailCell label="Data da Citação">
        {{ formatDateFromBackend(calculation?.criterion?.dateCitation) || '-' }}
      </ProjectDetailCell>
      <ProjectDetailCell label="Data de Ajuizamento da Recuperação Judicial">
        {{ formatDateFromBackend(calculation?.criterion?.dateRjFiling) || '-' }}
      </ProjectDetailCell>
      <ProjectDetailCell label="Data de Pedido da Recuperação Judicial">
        {{ formatDateFromBackend(calculation?.criterion?.dateRjRequest) || '-' }}
      </ProjectDetailCell>
    </QTabPanel>
  </QTabPanels>
</template>
