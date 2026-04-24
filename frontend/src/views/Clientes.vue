<script setup>
import { ref, onMounted, reactive } from 'vue'
import { api } from '../api'

const clientes = ref([])
const busca = ref('')
const carregando = ref(false)
const erro = ref('')
const ok = ref('')

const form = reactive(vazio())
const editandoId = ref(null)

function vazio() {
  return { nome: '', email: '', cpf: '', cnpj: '', telefone: '', observacoes: '', ativo: true }
}

async function carregar() {
  carregando.value = true
  erro.value = ''
  try {
    const { data } = await api.get('/api/clientes', { params: { q: busca.value || undefined } })
    clientes.value = data
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar clientes'
  } finally {
    carregando.value = false
  }
}

function editar(c) {
  editandoId.value = c.id
  Object.assign(form, c)
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

function cancelar() {
  editandoId.value = null
  Object.assign(form, vazio())
}

async function salvar() {
  erro.value = ''; ok.value = ''
  try {
    if (editandoId.value) {
      await api.put(`/api/clientes/${editandoId.value}`, form)
      ok.value = 'Cliente atualizado'
    } else {
      await api.post('/api/clientes', form)
      ok.value = 'Cliente criado'
    }
    cancelar()
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao salvar'
  }
}

async function remover(c) {
  if (!confirm(`Remover cliente "${c.nome}"?`)) return
  try {
    await api.delete(`/api/clientes/${c.id}`)
    await carregar()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao remover'
  }
}

onMounted(carregar)
</script>

<template>
  <div>
    <h2>Clientes</h2>

    <div v-if="erro" class="alert alert-err">{{ erro }}</div>
    <div v-if="ok"   class="alert alert-ok">{{ ok }}</div>

    <div class="card">
      <h3>{{ editandoId ? `Editando: ${form.nome}` : 'Novo cliente' }}</h3>
      <form @submit.prevent="salvar">
        <div class="row">
          <div>
            <label>Nome *</label>
            <input v-model="form.nome" required />
          </div>
          <div>
            <label>E-mail *</label>
            <input v-model="form.email" type="email" required />
          </div>
          <div>
            <label>CPF</label>
            <input v-model="form.cpf" placeholder="apenas números" />
          </div>
          <div>
            <label>CNPJ</label>
            <input v-model="form.cnpj" placeholder="apenas números" />
          </div>
          <div>
            <label>Telefone</label>
            <input v-model="form.telefone" />
          </div>
          <div>
            <label>Ativo</label>
            <select v-model="form.ativo">
              <option :value="true">Sim</option>
              <option :value="false">Não</option>
            </select>
          </div>
        </div>
        <div class="mt-2">
          <label>Observações</label>
          <textarea v-model="form.observacoes" />
        </div>
        <div class="mt-4 flex gap-2">
          <button type="submit" class="btn btn-primary">
            {{ editandoId ? 'Salvar alterações' : 'Criar cliente' }}
          </button>
          <button v-if="editandoId" type="button" class="btn btn-ghost" @click="cancelar">
            Cancelar
          </button>
        </div>
      </form>
    </div>

    <div class="card">
      <div class="flex items-center gap-2 mb-2">
        <h3 style="margin:0;">Lista</h3>
        <div class="spacer" />
        <input v-model="busca" placeholder="Buscar nome, e-mail, CPF..." style="max-width:300px" @keyup.enter="carregar" />
        <button class="btn btn-ghost btn-sm" @click="carregar">Buscar</button>
      </div>

      <table class="table" v-if="clientes.length">
        <thead>
          <tr>
            <th>Nome</th><th>E-mail</th><th>CPF</th><th>CNPJ</th><th>Telefone</th><th>Ativo</th><th></th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="c in clientes" :key="c.id">
            <td>{{ c.nome }}</td>
            <td>{{ c.email }}</td>
            <td>{{ c.cpf || '—' }}</td>
            <td>{{ c.cnpj || '—' }}</td>
            <td>{{ c.telefone || '—' }}</td>
            <td>{{ c.ativo ? 'Sim' : 'Não' }}</td>
            <td style="text-align:right; white-space:nowrap;">
              <button class="btn btn-ghost btn-sm" @click="editar(c)">Editar</button>
              <button class="btn btn-danger btn-sm" @click="remover(c)" style="margin-left:.3rem">Remover</button>
            </td>
          </tr>
        </tbody>
      </table>
      <p v-else-if="!carregando" class="text-muted">Nenhum cliente cadastrado.</p>
    </div>
  </div>
</template>
