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
const msgFull = ref('')
const intervaloSeg = ref(30)
const salvandoFull = ref(false)

const frasesEmail = ref('')
const msgFrases = ref('')
const salvandoFrases = ref(false)

async function carregar() {
  erro.value = ''
  msgFull.value = ''
  msgFrases.value = ''
  try {
    const [s, e] = await Promise.all([
      api.get('/api/status'),
      api.get('/api/envios', { params: { dias: 7 } }),
    ])
    status.value = s.data
    ultimos.value = e.data
    intervaloSeg.value = s.data.full_scan_interval_seconds ?? 30
    frasesEmail.value = s.data.email_frases_dashboard ?? ''
  } catch (err) {
    erro.value = err.response?.data?.detail || 'Não foi possível conectar à API'
  }
}

async function patchFull(payload) {
  if (!status.value?.full_env_enabled) return
  salvandoFull.value = true
  msgFull.value = ''
  try {
    const { data } = await api.patch('/api/settings/full', payload)
    status.value = data
    intervaloSeg.value = data.full_scan_interval_seconds
    msgFull.value = 'Guardado.'
  } catch (err) {
    msgFull.value = err.response?.data?.detail || 'Erro ao guardar'
    await carregar()
  } finally {
    salvandoFull.value = false
  }
}

async function salvarFrasesEmail() {
  salvandoFrases.value = true
  msgFrases.value = ''
  try {
    const { data } = await api.patch('/api/settings/email-frases', {
      email_frases_dashboard: frasesEmail.value,
    })
    status.value = data
    frasesEmail.value = data.email_frases_dashboard ?? ''
    msgFrases.value = 'Frases guardadas. Passam a ser usadas em todos os envios (FULL e avulso).'
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

async function aplicarIntervalo() {
  let n = Number(intervaloSeg.value)
  if (Number.isNaN(n)) n = 30
  n = Math.min(3600, Math.max(10, Math.round(n)))
  intervaloSeg.value = n
  await patchFull({ full_scan_interval_seconds: n })
}

watch(
  () => status.value?.full_scan_interval_seconds,
  (v) => {
    if (v != null) intervaloSeg.value = v
  }
)

watch(
  () => status.value?.email_frases_dashboard,
  (v) => {
    if (v !== undefined && v !== null && status.value) frasesEmail.value = v
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
      <div class="stat">
        <div class="label">Modo FULL (ativo)</div>
        <div class="value" :style="{ color: status.full_enabled ? 'var(--ok)' : 'var(--err)' }">
          {{ status.full_enabled ? 'ON' : 'OFF' }}
        </div>
        <small class="text-muted">Servidor + interruptor</small>
      </div>
      <div class="stat">
        <div class="label">Autenticação</div>
        <div class="value" :style="{ color: status.auth_enabled ? 'var(--ok)' : 'var(--warn)' }">
          {{ status.auth_enabled ? 'ATIVA' : 'DESATIVADA' }}
        </div>
      </div>
    </div>

    <div v-if="status" class="card card-full">
      <h3>Modo FULL (automático)</h3>
      <p class="text-muted mb-4" style="font-size: 0.92rem">
        Pasta vigiada:
        <code class="path-code">{{ status.full_watch_folder }}</code>
      </p>

      <div v-if="!status.full_env_enabled" class="alert alert-warn">
        O FULL está <strong>desligado no servidor</strong> (<code>FULL_ENABLED=false</code> no
        <code>.env</code>). O interruptor só fica disponível quando o administrador activar o FULL
        no ficheiro de configuração e reiniciar a API.
      </div>

      <template v-else>
        <div class="full-row">
          <div>
            <div class="full-label">Processar pasta automaticamente</div>
            <div class="text-muted" style="font-size: 0.85rem">
              Desligado = não varre nem envia; ligado = respeita o intervalo abaixo.
            </div>
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

        <div class="full-row full-row--interval mt-4">
          <div>
            <label class="full-label" for="int-full">Intervalo entre varreduras (segundos)</label>
            <div class="text-muted" style="font-size: 0.85rem">Entre 10 e 3600 segundos.</div>
          </div>
          <div class="interval-controls">
            <input
              id="int-full"
              type="number"
              min="10"
              max="3600"
              step="1"
              v-model.number="intervaloSeg"
              :disabled="salvandoFull"
              class="input-interval"
            />
            <button type="button" class="btn btn-primary btn-sm" :disabled="salvandoFull" @click="aplicarIntervalo">
              Aplicar
            </button>
          </div>
        </div>

        <p v-if="msgFull" class="text-muted mt-2" style="font-size: 0.88rem">{{ msgFull }}</p>
      </template>
    </div>

    <div v-if="status" class="card card-frases">
      <h3>Frases no e-mail</h3>
      <p class="text-muted mb-2" style="font-size: 0.92rem">
        Texto extra incluído no <strong>corpo</strong> de todos os envios (modo FULL e envio avulso),
        abaixo da mensagem principal. Pode usar várias linhas. Deixe vazio para não acrescentar nada.
      </p>
      <label class="full-label" for="tx-frases">Frases</label>
      <textarea
        id="tx-frases"
        v-model="frasesEmail"
        rows="6"
        :disabled="salvandoFrases"
        placeholder="Ex.: Agradecemos a preferência. Em caso de sinistro, contacte o número..."
        class="textarea-frases"
      />
      <div class="mt-2 flex gap-2 items-center">
        <button type="button" class="btn btn-primary" :disabled="salvandoFrases" @click="salvarFrasesEmail">
          Guardar frases
        </button>
        <span v-if="msgFrases" class="text-muted" style="font-size: 0.88rem">{{ msgFrases }}</span>
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
