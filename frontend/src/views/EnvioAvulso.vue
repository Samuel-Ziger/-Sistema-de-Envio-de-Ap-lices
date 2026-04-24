<script setup>
import { ref, onMounted, reactive } from 'vue'
import { api } from '../api'

const clientes = ref([])
const clienteId = ref(null)
const criarNovo = ref(false)
const novoCliente = reactive({ nome: '', email: '', cpf: '', cnpj: '', telefone: '' })
const numeroApolice = ref('')
const assunto = ref('')
const mensagem = ref('')
const extrairDados = ref(true)
const arquivo = ref(null)
const enviando = ref(false)
const erro = ref('')
const ok = ref('')
const ultimoEnvio = ref(null)

async function carregarClientes() {
  const { data } = await api.get('/api/clientes', { params: { ativo: true } })
  clientes.value = data
}

function onFile(e) {
  arquivo.value = e.target.files[0] || null
}

async function enviar() {
  erro.value = ''; ok.value = ''; ultimoEnvio.value = null
  if (!arquivo.value) { erro.value = 'Selecione o PDF'; return }
  if (!criarNovo.value && !clienteId.value) { erro.value = 'Selecione ou crie um cliente'; return }
  if (criarNovo.value && (!novoCliente.nome || !novoCliente.email)) {
    erro.value = 'Nome e e-mail do novo cliente são obrigatórios'
    return
  }

  const fd = new FormData()
  fd.append('arquivo', arquivo.value)
  if (criarNovo.value) {
    fd.append('cliente_novo', JSON.stringify(novoCliente))
  } else {
    fd.append('cliente_id', clienteId.value)
  }
  if (numeroApolice.value) fd.append('numero_apolice', numeroApolice.value)
  if (assunto.value) fd.append('assunto', assunto.value)
  if (mensagem.value) fd.append('mensagem', mensagem.value)
  fd.append('extrair_dados', extrairDados.value ? 'true' : 'false')

  enviando.value = true
  try {
    const { data } = await api.post('/api/envios/avulso', fd, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    ultimoEnvio.value = data
    if (data.status === 'enviado') {
      ok.value = `Enviado com sucesso para ID ${data.cliente_id}`
    } else {
      erro.value = `Envio registrado com status "${data.status}": ${data.erro_msg || ''}`
    }
    await carregarClientes()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha no envio'
  } finally {
    enviando.value = false
  }
}

onMounted(carregarClientes)
</script>

<template>
  <div>
    <h2>Envio Avulso</h2>
    <p class="text-muted">Selecione um cliente existente (ou cadastre na hora), envie o PDF e o sistema dispara o e-mail imediatamente.</p>

    <div v-if="erro" class="alert alert-err">{{ erro }}</div>
    <div v-if="ok"   class="alert alert-ok">{{ ok }}</div>

    <form @submit.prevent="enviar">
      <div class="card">
        <h3>Cliente</h3>
        <div class="flex gap-4 mb-2">
          <label style="display:flex; align-items:center; gap:.4rem;">
            <input type="radio" :value="false" v-model="criarNovo" /> Selecionar existente
          </label>
          <label style="display:flex; align-items:center; gap:.4rem;">
            <input type="radio" :value="true" v-model="criarNovo" /> Cadastrar novo agora
          </label>
        </div>

        <div v-if="!criarNovo">
          <label>Cliente</label>
          <select v-model="clienteId">
            <option :value="null">— selecione —</option>
            <option v-for="c in clientes" :key="c.id" :value="c.id">
              {{ c.nome }} — {{ c.email }}
            </option>
          </select>
        </div>

        <div v-else class="row">
          <div>
            <label>Nome *</label>
            <input v-model="novoCliente.nome" required />
          </div>
          <div>
            <label>E-mail *</label>
            <input v-model="novoCliente.email" type="email" required />
          </div>
          <div>
            <label>CPF</label>
            <input v-model="novoCliente.cpf" />
          </div>
          <div>
            <label>CNPJ</label>
            <input v-model="novoCliente.cnpj" />
          </div>
          <div>
            <label>Telefone</label>
            <input v-model="novoCliente.telefone" />
          </div>
        </div>
      </div>

      <div class="card">
        <h3>Arquivo & mensagem</h3>
        <div class="row">
          <div>
            <label>PDF da apólice *</label>
            <input type="file" accept="application/pdf" @change="onFile" required />
          </div>
          <div>
            <label>Nº da apólice (opcional)</label>
            <input v-model="numeroApolice" placeholder="Se vazio, tenta extrair do PDF" />
          </div>
        </div>
        <div class="row mt-2">
          <div>
            <label>Assunto (opcional)</label>
            <input v-model="assunto" placeholder="Default: Envio de Apolice - <número>" />
          </div>
          <div>
            <label>Extrair dados do PDF?</label>
            <select v-model="extrairDados">
              <option :value="true">Sim</option>
              <option :value="false">Não</option>
            </select>
          </div>
        </div>
        <div class="mt-2">
          <label>Mensagem adicional</label>
          <textarea v-model="mensagem" />
        </div>
      </div>

      <button type="submit" class="btn btn-accent" :disabled="enviando">
        {{ enviando ? 'Enviando...' : 'Enviar agora' }}
      </button>
    </form>

    <div v-if="ultimoEnvio" class="card mt-4">
      <h3>Último envio</h3>
      <p>ID: <strong>{{ ultimoEnvio.id }}</strong></p>
      <p>Status: <span class="badge" :class="ultimoEnvio.status">{{ ultimoEnvio.status }}</span></p>
      <p v-if="ultimoEnvio.erro_msg" class="text-muted">Erro: {{ ultimoEnvio.erro_msg }}</p>
    </div>
  </div>
</template>
