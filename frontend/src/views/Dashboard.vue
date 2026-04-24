<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { api } from '../api'

const dataRelogio = ref('')
const horaRelogio = ref('')
let timerRelogio = null

function atualizarRelogio() {
  const d = new Date()
  dataRelogio.value = d.toLocaleDateString('pt-BR', {
    weekday: 'short',
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
  horaRelogio.value = d.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
  })
}

const status = ref(null)
const ultimos = ref([])
const erro = ref('')
const salvandoFull = ref(false)
const salvandoHoraFull = ref(false)
const msgHoraFull = ref('')
const horaExecucaoFull = ref('08:00')

const frasesEmail = ref('')
const msgFrases = ref('')
const salvandoFrases = ref(false)
const editandoFrase = ref(false)

async function carregar() {
  erro.value = ''
  msgFrases.value = ''
  try {
    const [s, e] = await Promise.all([
      api.get('/api/status'),
      api.get('/api/envios', { params: { dias: 7 } }),
    ])
    status.value = s.data
    ultimos.value = e.data
    frasesEmail.value = s.data.email_frases_dashboard ?? ''
    editandoFrase.value = !Boolean((s.data.email_frases_dashboard ?? '').trim())
    horaExecucaoFull.value = s.data.full_scan_exec_time ?? '08:00'
  } catch (err) {
    erro.value = err.response?.data?.detail || 'Não foi possível conectar à API'
  }
}

async function patchFull(payload) {
  salvandoFull.value = true
  try {
    const { data } = await api.patch('/api/settings/full', payload)
    status.value = data
  } catch (err) {
    erro.value = err.response?.data?.detail || 'Erro ao guardar o modo FULL'
    await carregar()
  } finally {
    salvandoFull.value = false
  }
}

async function salvarFrasesEmail() {
  salvandoFrases.value = true
  msgFrases.value = ''
  try {
    const frase = (frasesEmail.value || '').replace(/\s+/g, ' ').trim()
    if (!frase) {
      msgFrases.value = 'Informe uma frase antes de guardar.'
      return
    }
    const { data } = await api.patch('/api/settings/email-frases', {
      email_frases_dashboard: frase,
    })
    status.value = data
    frasesEmail.value = data.email_frases_dashboard ?? ''
    editandoFrase.value = false
    msgFrases.value = 'Frase guardada.'
  } catch (err) {
    msgFrases.value = err.response?.data?.detail || 'Erro ao guardar'
    await carregar()
  } finally {
    salvandoFrases.value = false
  }
}

async function onToggleFull(ativado) {
  await patchFull({ full_scan_active: ativado })
}

async function salvarHoraExecucaoFull() {
  msgHoraFull.value = ''
  if (!/^\d{2}:\d{2}$/.test(horaExecucaoFull.value || '')) {
    msgHoraFull.value = 'Informe um horário válido (HH:MM).'
    return
  }
  salvandoHoraFull.value = true
  try {
    const { data } = await api.patch('/api/settings/full', {
      full_scan_exec_time: horaExecucaoFull.value,
    })
    status.value = data
    horaExecucaoFull.value = data.full_scan_exec_time ?? horaExecucaoFull.value
    msgHoraFull.value = 'Horário de execução do FULL guardado.'
  } catch (err) {
    msgHoraFull.value = err.response?.data?.detail || 'Erro ao guardar horário'
    await carregar()
  } finally {
    salvandoHoraFull.value = false
  }
}

watch(
  () => status.value?.email_frases_dashboard,
  (v) => {
    if (v !== undefined && v !== null && status.value) frasesEmail.value = v
  }
)

watch(
  () => status.value?.full_scan_exec_time,
  (v) => {
    if (v) horaExecucaoFull.value = v
  }
)

onMounted(() => {
  carregar()
  atualizarRelogio()
  timerRelogio = setInterval(atualizarRelogio, 1000)
})

onUnmounted(() => {
  if (timerRelogio) clearInterval(timerRelogio)
})
</script>

<template>
  <div>
    <div class="app-topbar">
      <h2>Dashboard</h2>
      <div class="topbar-right">
        <div class="dash-clock" aria-live="polite">
          <span class="dash-clock__date">{{ dataRelogio }}</span>
          <span class="dash-clock__time">{{ horaRelogio }}</span>
        </div>
        <button type="button" class="btn btn-ghost btn-sm" @click="carregar">Atualizar</button>
      </div>
    </div>

    <div v-if="erro" class="alert alert-err">{{ erro }}</div>

    <div v-if="status" class="grid-cards mb-4">
      <div class="stat">
        <div class="label">Clientes</div>
        <div class="value">{{ status.total_clientes }}</div>
      </div>
      <div class="stat">
        <div class="label">Envios (total)</div>
        <div class="value">{{ status.total_envios }}</div>
      </div>
      <div class="stat stat--modo-full">
        <div class="label">Modo FULL (ativo)</div>
        <div class="stat-full-row">
          <div
            class="value"
            :style="{ color: status.full_scan_active ? 'var(--ok)' : 'var(--err)' }"
          >
            {{ status.full_scan_active ? 'ON' : 'OFF' }}
          </div>
          <label class="switch" :class="{ 'switch--disabled': salvandoFull }">
            <input
              type="checkbox"
              role="switch"
              :checked="status.full_scan_active"
              :disabled="salvandoFull"
              @change="onToggleFull($event.target.checked)"
            />
            <span class="switch-slider" />
          </label>
        </div>
      </div>
      <div class="stat">
        <div class="label">Autenticação</div>
        <div class="value" :style="{ color: status.auth_enabled ? 'var(--ok)' : 'var(--warn)' }">
          {{ status.auth_enabled ? 'ATIVA' : 'DESATIVADA' }}
        </div>
      </div>
    </div>

    <div v-if="status" class="card card-frases">
      <h3>Horário de execução do FULL</h3>
      <label class="full-label" for="hora-full">Hora (HH:MM)</label>
      <div class="full-time-row">
        <input
          id="hora-full"
          v-model="horaExecucaoFull"
          type="time"
          :disabled="salvandoHoraFull"
          step="60"
          class="input-time"
        />
        <button
          type="button"
          class="btn btn-primary"
          :disabled="salvandoHoraFull"
          @click="salvarHoraExecucaoFull"
        >
          Definir hora
        </button>
      </div>
      <div class="mt-2">
        <span v-if="msgHoraFull" class="text-muted" style="font-size: 0.88rem">{{ msgHoraFull }}</span>
      </div>
    </div>

    <div v-if="status" class="card card-frases">
      <h3>Frases no e-mail</h3>
      <p class="text-muted mb-2" style="font-size: 0.92rem">
        A frase é obrigatória para envio no modo FULL e avulso.
      </p>
      <div v-if="editandoFrase">
        <label class="full-label" for="tx-frases">Frase</label>
        <input
          id="tx-frases"
          v-model="frasesEmail"
          :disabled="salvandoFrases"
          placeholder="Ex.: Agradecemos a preferência."
          maxlength="300"
        />
        <div class="mt-2 flex gap-2 items-center">
          <button type="button" class="btn btn-primary" :disabled="salvandoFrases" @click="salvarFrasesEmail">
            Guardar frase
          </button>
          <span v-if="msgFrases" class="text-muted" style="font-size: 0.88rem">{{ msgFrases }}</span>
        </div>
      </div>
      <div v-else>
        <p class="text-muted" style="font-size: 0.95rem; margin: 0 0 0.5rem 0">
          <strong>Frase atual:</strong> {{ status.email_frases_dashboard || '—' }}
        </p>
        <button type="button" class="btn btn-ghost btn-sm" @click="editandoFrase = true">
          Editar frase
        </button>
      </div>
    </div>

    <div class="card">
      <h3>Últimos envios (7 dias)</h3>
      <table class="table" v-if="ultimos.length">
        <thead>
          <tr>
            <th>#</th><th>Tipo</th><th>Arquivo</th><th>Apólice</th>
            <th>Status</th><th>Quando</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in ultimos" :key="e.id">
            <td>{{ e.id }}</td>
            <td><span class="badge" :class="e.tipo_envio">{{ e.tipo_envio }}</span></td>
            <td>{{ e.nome_arquivo_original || e.nome_arquivo_final || '—' }}</td>
            <td>{{ e.numero_apolice || '—' }}</td>
            <td><span class="badge" :class="e.status">{{ e.status }}</span></td>
            <td>{{ new Date(e.criado_em).toLocaleString() }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="text-muted">Nenhum envio nos últimos 7 dias.</p>
    </div>
  </div>
</template>
