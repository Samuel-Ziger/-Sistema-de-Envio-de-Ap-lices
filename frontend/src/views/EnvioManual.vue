<script setup>
import { ref, onMounted, reactive, computed, watch } from 'vue'
import { api } from '../api'

const clientes = ref([])
const autos = ref([])
const tipos = ref([])
const corpos = ref([])
const assinaturas = ref([])

const clienteId = ref(null)
const criarNovo = ref(false)
const novoCliente = reactive({ nome: '', email: '', cpf: '', cnpj: '', telefone: '' })
const numeroApolice = ref('')
const extrairDados = ref(true)
const tipoCodigo = ref('')
const autoId = ref(null)
const corpoEmailId = ref(null)
const assinaturaId = ref(null)
const arquivo = ref(null)
const boleto = ref(null)
const enviando = ref(false)
const demonstrando = ref(false)
const erro = ref('')
const ok = ref('')
const ultimoEnvio = ref(null)
const demo = ref(null)

const autosCliente = computed(() =>
  clienteId.value ? autos.value.filter((a) => a.cliente_id === clienteId.value) : []
)

async function carregarOpcoes() {
  const [c, t, co, a, au] = await Promise.all([
    api.get('/api/clientes', { params: { ativo: true } }),
    api.get('/api/tipos-envio', { params: { ativo: true } }),
    api.get('/api/corpos-email', { params: { ativo: true } }),
    api.get('/api/assinaturas', { params: { ativo: true } }),
    api.get('/api/autos', { params: { ativo: true } }),
  ])
  clientes.value = c.data
  tipos.value = t.data
  corpos.value = co.data
  assinaturas.value = a.data
  autos.value = au.data
}

watch(clienteId, () => {
  autoId.value = null
})

function onArquivo(e) { arquivo.value = e.target.files[0] || null }
function onBoleto(e)  { boleto.value  = e.target.files[0] || null }

function montarFormData() {
  const fd = new FormData()
  if (arquivo.value) fd.append('arquivo', arquivo.value)
  if (boleto.value)  fd.append('boleto', boleto.value)
  if (criarNovo.value) {
    fd.append('cliente_novo', JSON.stringify(novoCliente))
  } else if (clienteId.value) {
    fd.append('cliente_id', clienteId.value)
  }
  if (numeroApolice.value) fd.append('numero_apolice', numeroApolice.value)
  fd.append('extrair_dados', extrairDados.value ? 'true' : 'false')
  if (tipoCodigo.value)    fd.append('tipo_codigo', tipoCodigo.value)
  if (autoId.value)        fd.append('auto_id', autoId.value)
  if (corpoEmailId.value)  fd.append('corpo_email_id', corpoEmailId.value)
  if (assinaturaId.value)  fd.append('assinatura_id', assinaturaId.value)
  return fd
}

function validar({ exigirArquivo }) {
  if (exigirArquivo && !arquivo.value) { erro.value = 'Selecione o PDF da apólice'; return false }
  if (!criarNovo.value && !clienteId.value) { erro.value = 'Selecione ou crie um cliente'; return false }
  if (criarNovo.value && (!novoCliente.nome || !novoCliente.email)) {
    erro.value = 'Nome e e-mail do novo cliente são obrigatórios'; return false
  }
  return true
}

async function enviar() {
  erro.value = ''; ok.value = ''; ultimoEnvio.value = null
  if (!validar({ exigirArquivo: true })) return
  enviando.value = true
  try {
    const { data } = await api.post('/api/envios/manual', montarFormData(), {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    ultimoEnvio.value = data
    if (data.status === 'enviado') ok.value = `Enviado com sucesso para cliente ${data.cliente_id}`
    else erro.value = `Status "${data.status}": ${data.erro_msg || ''}`
    await carregarOpcoes()
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha no envio'
  } finally {
    enviando.value = false
  }
}

async function demonstrar() {
  erro.value = ''; demo.value = null
  if (!validar({ exigirArquivo: false })) return
  demonstrando.value = true
  try {
    const { data } = await api.post('/api/envios/demonstrar', montarFormData(), {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    demo.value = data
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Não foi possível gerar a demonstração'
  } finally {
    demonstrando.value = false
  }
}

onMounted(carregarOpcoes)
</script>

<template>
  <div>
    <h2>Envio Manual</h2>
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
          <div><label>Nome *</label><input v-model="novoCliente.nome" required /></div>
          <div><label>E-mail *</label><input v-model="novoCliente.email" type="email" required /></div>
          <div><label>CPF</label><input v-model="novoCliente.cpf" /></div>
          <div><label>CNPJ</label><input v-model="novoCliente.cnpj" /></div>
          <div><label>Telefone</label><input v-model="novoCliente.telefone" /></div>
        </div>
      </div>

      <div class="card">
        <h3>Arquivo &amp; mensagem</h3>
        <div class="row">
          <div>
            <label>PDF da apólice *</label>
            <input type="file" accept="application/pdf" @change="onArquivo" />
          </div>
          <div>
            <label>Boleto (opcional)</label>
            <input type="file" accept="application/pdf" @change="onBoleto" />
          </div>
          <div>
            <label>Nº da apólice (opcional)</label>
            <input v-model="numeroApolice" placeholder="Se vazio, tenta extrair do PDF" />
          </div>
          <div>
            <label>Tipo de envio</label>
            <select v-model="tipoCodigo">
              <option value="">Sem tipo específico</option>
              <option v-for="t in tipos" :key="t.id" :value="t.codigo">{{ t.nome }}</option>
            </select>
          </div>
        </div>

        <div class="row mt-2">
          <div>
            <label>Extrair dados do PDF?</label>
            <select v-model="extrairDados">
              <option :value="true">Sim</option>
              <option :value="false">Não</option>
            </select>
          </div>
          <div v-if="autosCliente.length">
            <label>Veículo (auto)</label>
            <select v-model="autoId">
              <option :value="null">— nenhum —</option>
              <option v-for="a in autosCliente" :key="a.id" :value="a.id">
                {{ a.placa }} {{ a.marca ? '· ' + a.marca : '' }} {{ a.modelo ? '· ' + a.modelo : '' }}
              </option>
            </select>
          </div>
          <div>
            <label>Corpo de e-mail</label>
            <select v-model="corpoEmailId">
              <option :value="null">Padrão (do tipo de envio)</option>
              <option v-for="c in corpos" :key="c.id" :value="c.id">{{ c.nome }}</option>
            </select>
          </div>
          <div>
            <label>Assinatura</label>
            <select v-model="assinaturaId">
              <option :value="null">Sem assinatura</option>
              <option v-for="a in assinaturas" :key="a.id" :value="a.id">{{ a.nome }}</option>
            </select>
          </div>
        </div>

        <p class="text-muted mt-2" style="font-size: 0.9rem">
          O envio manual usa obrigatoriamente as frases configuradas no Dashboard.
        </p>
      </div>

      <div class="flex gap-2">
        <button type="submit" class="btn btn-accent" :disabled="enviando">
          {{ enviando ? 'Enviando...' : 'Enviar agora' }}
        </button>
        <button type="button" class="btn btn-ghost" :disabled="demonstrando" @click="demonstrar">
          {{ demonstrando ? 'Gerando...' : 'Demonstrar e-mail' }}
        </button>
      </div>
    </form>

    <div v-if="demo" class="card mt-4">
      <h3>Demonstração do e-mail</h3>
      <p><strong>De:</strong> {{ demo.de }}</p>
      <p><strong>Para:</strong> {{ demo.para }}</p>
      <p><strong>Assunto:</strong> {{ demo.assunto }}</p>
      <hr />
      <div class="email-preview" v-html="demo.html"></div>
    </div>

    <div v-if="ultimoEnvio" class="card mt-4">
      <h3>Último envio</h3>
      <p>ID: <strong>{{ ultimoEnvio.id }}</strong></p>
      <p>Status: <span class="badge" :class="ultimoEnvio.status">{{ ultimoEnvio.status }}</span></p>
      <p v-if="ultimoEnvio.erro_msg" class="text-muted">Erro: {{ ultimoEnvio.erro_msg }}</p>
    </div>
  </div>
</template>

<style scoped>
.email-preview {
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem;
  background: #fafafa;
}
</style>
