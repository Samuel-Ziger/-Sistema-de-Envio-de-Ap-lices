<script setup>
import { ref, onMounted, reactive } from 'vue'
import { api } from '../api'

const envios = ref([])
const filtros = reactive({ tipo: '', status: '', dias: 30 })
const erro = ref('')

async function carregar() {
  erro.value = ''
  try {
    const params = {}
    if (filtros.tipo) params.tipo = filtros.tipo
    if (filtros.status) params.status = filtros.status
    if (filtros.dias) params.dias = filtros.dias
    const { data } = await api.get('/api/envios', { params })
    envios.value = data
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Erro ao carregar'
  }
}

onMounted(carregar)
</script>

<template>
  <div>
    <h2>Histórico de envios</h2>
    <div v-if="erro" class="alert alert-err">{{ erro }}</div>

    <div class="card">
      <div class="row">
        <div>
          <label>Tipo</label>
          <select v-model="filtros.tipo">
            <option value="">Todos</option>
            <option value="FULL">FULL</option>
            <option value="AVULSO">AVULSO</option>
          </select>
        </div>
        <div>
          <label>Status</label>
          <select v-model="filtros.status">
            <option value="">Todos</option>
            <option value="enviado">Enviado</option>
            <option value="erro">Erro</option>
            <option value="pendente">Pendente</option>
          </select>
        </div>
        <div>
          <label>Últimos N dias</label>
          <input type="number" min="1" v-model.number="filtros.dias" />
        </div>
        <div style="display:flex; align-items:flex-end;">
          <button class="btn btn-primary" @click="carregar">Filtrar</button>
        </div>
      </div>
    </div>

    <div class="card">
      <table class="table" v-if="envios.length">
        <thead>
          <tr>
            <th>ID</th><th>Tipo</th><th>Cliente</th><th>Arquivo</th>
            <th>Apólice</th><th>Status</th><th>Criado</th><th>Enviado</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="e in envios" :key="e.id">
            <td>{{ e.id }}</td>
            <td><span class="badge" :class="e.tipo_envio">{{ e.tipo_envio }}</span></td>
            <td>#{{ e.cliente_id }}</td>
            <td>{{ e.nome_arquivo_original || '—' }}</td>
            <td>{{ e.numero_apolice || '—' }}</td>
            <td>
              <span class="badge" :class="e.status">{{ e.status }}</span>
              <div v-if="e.erro_msg" class="text-muted" style="font-size:.75rem;">{{ e.erro_msg }}</div>
            </td>
            <td>{{ new Date(e.criado_em).toLocaleString() }}</td>
            <td>{{ e.enviado_em ? new Date(e.enviado_em).toLocaleString() : '—' }}</td>
          </tr>
        </tbody>
      </table>
      <p v-else class="text-muted">Nenhum envio encontrado.</p>
    </div>
  </div>
</template>
