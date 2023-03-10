<script setup lang="ts">
const router = useRouter()

const filterBy = $ref('')
let loading = $ref(false)
let showModal = $ref(false)

const defaultUser = {
  name: '',
  email: '',
  groups: [],
}
const form = ref(null) as any
let groups: any = $ref([])
let userEditing = $ref(clone(defaultUser))
let users: any[] = $ref([])

const pendingRequests = computed(() => users.filter(({ isActive }) => !isActive).length)

const loadPage = async () => {
  loading = true
  try {
    users = await usersService.getUsers()
    groups = await usersService.getGroups()
  }
  catch (error) {
    throwError(error)
  }
  finally {
    loading = false
  }
}
onMounted(() => loadPage())

const editUser = async (user: any) => {
  userEditing = clone(user)
  userEditing.groups = userEditing.groups.map(({ id }: any) => id)
  showModal = true
  await delay(0.01)
  form.value.resetValidation()
}
const clearUser = async () => {
  await delay(0.5)
  userEditing = clone(defaultUser)
}
const updateUser = async () => {
  try {
    await usersService.setPermission(userEditing)
    showModal = false
    notify({
      message: userEditing ? 'Usuário Atualizado!' : 'Usuário Cadastrado',
      timeout: 5,
    })
    loadPage()
  }
  catch (error) {
    throwError(error)
  }
  finally {
    loading = false
  }
}

const columns = [
  {
    name: 'name',
    field: 'name',
    label: 'Usuário',
    required: true,
    align: 'left',
    sortable: true,
  },
  {
    name: 'groups',
    field: 'groups',
    label: 'Permissões',
    align: 'left',
    format: (value: any[]) => value.map(({ name }: any) => name),
    sortable: true,
  },
  {
    name: 'action',
    field: 'isActive',
    label: 'Ação',
    align: 'center',
    sortable: true,
    style: 'width: 100px',
  },
] as {
  name: string
  label: string
  field: string
  required?: boolean
  align?: 'left' | 'right' | 'center'
  sortable?: boolean
}[]
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
        <div class="flex items-center gap-2">
          <h1 class="font-bold text-4xl">
            {{ `Solicitações (${pendingRequests})` }}
          </h1>
          <ReloadBtn
            hint="Recarregar a Lista de Usuários"
            @click="loadPage"
          />
        </div>
        <SearchFilter v-model="filterBy" />
      </div>

      <QTable
        class="my-header-table"
        :rows="users"
        :columns="columns"
        :loading="loading"
        :filter="filterBy"
        row-key="id"
        flat
        bordered
      >
        hide-header
        <template #body-cell-name="props">
          <q-td :props="props">
            <div class="flex no-wrap items-center gap-3 font-bold py-2">
              <Img
                v-if="props.row.picture"
                :src="`data:image/jpeg;base64,${props.row.picture}`"
                :error-image="`${baseUrl}/fallback/user.svg`"
                class="h-10 w-10 rounded-.5 object-cover"
              />
              <div 
                v-else 
                class="h-10 w-10 rounded-.5 mr-2 bg-gray-2 rounded-.5 flex justify-center items-center text-[16px]"
              >
                {{ getInitials(props.value) }}
              </div>
              <div class="font-medium">
                <div class="text-lg font-bold">
                  {{ props.value }}
                </div>
                <div>
                  {{ props.row.email }}
                </div>
              </div>
            </div>
          </q-td>
        </template>

        <template #body-cell-groups="props">
          <q-td :props="props">
            <div class="flex gap-2">
              <div
                v-for="group in props.value"
                :key="group"
                class="rounded-full px-3 py-1 border-1 border--primary/12 bg--primary/50 whitespace-nowrap"
              >
                {{ group }}
              </div>
            </div>
          </q-td>
        </template>

        <template #body-cell-action="props">
          <q-td :props="props">
            <div class="flex justify-end">
              <Btn
                :label="props.value ? 'Editar' : 'Cadastrar'"
                :outlined="props.value"
                @click="editUser(props.row)"
              >
                <div class="i-carbon-chevron-right" />
              </Btn>
            </div>
          </q-td>
        </template>
      </QTable>
    </div>
  </div>
  <Modal
    v-model="showModal"
    :title="`Solicitação de ${userEditing.name}`"
    modal-class="max-w-120"
    :close-disabled="loading"
    @close="clearUser"
  >
    <QForm ref="form" @submit="updateUser">
      <div class="px-4 pb-4">
        <div class="text-xl mb-4">
          Email: {{ userEditing.email }}
        </div>
        <QSelect
          v-model="userEditing.groups"
          label="Permissões"
          multiple
          outlined
          option-label="name"
          option-value="id"
          emit-value
          map-options
          :rules="[(values) => values.length >= 1 || 'É necessário escolher no mínimo 1 grupo para o usuário!']"
          :options="groups"
        >
          <template #selected-item="{ opt, index, removeAtIndex }">
            <div class="flex no-wrap items-center gap-2 bg--primary/20 rounded-full pl-3 pr-1 py-1 border-1 border--primary/12">
              {{ opt.name }}
              <div
                class="rounded-full bg-white/20 hover:bg-white/50 min-h-5 min-w-5 flex justify-center items-center cursor-pointer"
                @click="removeAtIndex(index)"
              >
                <div class="i-carbon-close" />
              </div>
            </div>
          </template>
        </QSelect>
      </div>
      <div class="flex justify-end border-t-1 border-black/12 p-4">
        <Btn
          :label="userEditing.isActive ? 'Atualizar' : 'Cadastrar'"
          :loading-label="userEditing.isActive ? 'Atualizando...' : 'Cadastrando...'"
          :loading="loading"
          type="submit"
        />
      </div>
    </QForm>
  </Modal>
</template>

<route lang="yaml">
meta:
  permissions: [view_user]
</route>
