<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api'

const status = ref(null)
const ultimos = ref([])
const erro = ref('')

async function carregar() {
  erro.value = ''
  try {
    const [s, e] = await Promise.all([
      api.get('/api/status'),
      api.get('/api/envios', { params: { dias: 7 } }),
    ])
    status.value = s.data
    ultimos.value = e.data
  } catch (err) {
    erro.value = err.response?.data?.detail || 'Não foi possível conectar à API'
  }
}

onMounted(carregar)
</script>

<template>
  <div>
    <div class="app-topbar">
      <h2>Dashboard</h2>
      <button class="btn btn-ghost btn-sm" @click="carregar">Atualizar</button>
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
        <div class="label">Modo FULL</div>
        <div class="value" :style="{color: status.full_enabled ? 'var(--ok)' : 'var(--err)'}">
          {{ status.full_enabled ? 'ON' : 'OFF' }}
        </div>
        <small class="text-muted">{{ status.full_watch_folder }}</small>
      </div>
      <div class="stat">
        <div class="label">Autenticação</div>
        <div class="value" :style="{color: status.auth_enabled ? 'var(--ok)' : 'var(--warn)'}">
          {{ status.auth_enabled ? 'ATIVA' : 'DESATIVADA' }}
        </div>
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
