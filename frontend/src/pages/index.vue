<script setup lang="ts">
const router = useRouter()
</script>

<template>
  <div class="grid sm:grid-cols-2 gap-16 max-w-300 px-6 flex-1 mx-auto">
    <div class="flex flex-col justify-center gap-6">
      <h1 class="font-extrabold text-6xl mt-8">
        JUCA
      </h1>
      <h2 class="text-gray text-3xl">
        Sistema de Recuperação Financeira
      </h2>
      <p>
        D.JUD simplifica os cálculos financeiros complexos necessários nessas operações, fornecendo resultados precisos e confiáveis ao longo do tempo. Com sua interface amigável e algoritmos avançados, é a ferramenta ideal para advogados, analistas financeiros e demais profissionais envolvidos em processos de recuperação judicial e falência.
        Para assistir ao tutorial de uso da ferramenta Clique aqui
      </p>
      <div class="flex flex-wrap gap-3">
        <Btn @click="router.push('/home')">
          Entrar
        </Btn>
        <Btn color="secondary">
          Solicitar acesso
        </Btn>
        <Btn transparent>
          Solicitando acesso
          <Spinner />
        </Btn>
      </div>
    </div>
    <div class="px-8">
      <Img src="/illustrations/splash-balance.svg" class="h-full min-h-10" />
    </div>
  </div>
</template>

<route lang="yaml">
meta:
  layout: splash
</route>
