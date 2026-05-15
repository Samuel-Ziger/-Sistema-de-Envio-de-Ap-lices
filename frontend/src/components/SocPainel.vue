<script setup>
import { ref, computed, watch } from 'vue'
import { api } from '../api'

const props = defineProps({
  status: { type: Object, default: null },
})

const emit = defineEmits(['atualizado'])

const ativarAberto = ref(false)
const desativarAberto = ref(false)
const chave = ref('')
const chave2 = ref('')
const chaveDesativar = ref('')
const motivo = ref('Suspeita de invasão ou ataque')
const erro = ref('')
const ok = ref('')
const processando = ref(false)

const socAtivo = computed(() => Boolean(props.status?.soc_mode_active))

watch(
  () => props.status?.soc_mode_active,
  (v) => {
    if (v) {
      ativarAberto.value = false
    }
  }
)

async function ativar() {
  erro.value = ''
  ok.value = ''
  if (chave.value.length < 8) {
    erro.value = 'A chave de emergência deve ter pelo menos 8 caracteres'
    return
  }
  if (chave.value !== chave2.value) {
    erro.value = 'As chaves não coincidem'
    return
  }
  if (
    !confirm(
      'ATIVAR MODO SOC?\n\n• Todos os envios serão bloqueados\n• Os dados dos clientes serão recifrados com a nova chave\n• Guarde a chave num local seguro — só ela desativa o modo\n\nContinuar?'
    )
  ) {
    return
  }
  processando.value = true
  try {
    const { data } = await api.post('/api/soc/ativar', {
      chave_soc: chave.value,
      chave_soc_confirmacao: chave2.value,
      motivo: motivo.value,
    })
    ok.value = data.mensagem
    chave.value = ''
    chave2.value = ''
    ativarAberto.value = false
    emit('atualizado')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha ao ativar modo SOC'
  } finally {
    processando.value = false
  }
}

async function desativar() {
  erro.value = ''
  ok.value = ''
  if (!chaveDesativar.value) {
    erro.value = 'Informe a chave de emergência'
    return
  }
  processando.value = true
  try {
    const { data } = await api.post('/api/soc/desativar', {
      chave_soc: chaveDesativar.value,
    })
    ok.value = data.mensagem
    chaveDesativar.value = ''
    desativarAberto.value = false
    emit('atualizado')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Chave incorreta ou falha ao desativar'
  } finally {
    processando.value = false
  }
}
</script>

<template>
  <section class="card soc-painel" :class="{ 'soc-painel--ativo': socAtivo }">
    <h3>Modo SOC (resposta a incidente)</h3>

    <div v-if="socAtivo" class="alert alert-err soc-banner">
      <strong>MODO SOC ATIVO</strong> — envios e operações bloqueados.
      <span v-if="status?.soc_motivo"> Motivo: {{ status.soc_motivo }}</span>
      <span v-if="status?.soc_ativado_em" class="d-block mt-1" style="font-size: 0.85rem">
        Desde: {{ status.soc_ativado_em }}
      </span>
    </div>

    <p v-else class="text-muted" style="font-size: 0.9rem">
      Em caso de ataque: ative o SOC para parar todos os envios e recifrar os clientes com uma
      <strong>chave de emergência diferente</strong> da senha do <code>.env</code>.
      PDFs maliciosos na pasta não serão enviados enquanto o modo estiver ativo.
    </p>

    <div v-if="erro" class="alert alert-err">{{ erro }}</div>
    <div v-if="ok" class="alert alert-ok">{{ ok }}</div>

    <div v-if="!socAtivo" class="flex gap-2 flex-wrap">
      <button type="button" class="btn btn-danger" @click="ativarAberto = true">
        Ativar modo SOC
      </button>
    </div>

    <div v-else class="flex gap-2">
      <button type="button" class="btn btn-accent" @click="desativarAberto = true">
        Desativar modo SOC (chave de emergência)
      </button>
    </div>

    <div v-if="ativarAberto && !socAtivo" class="modal-backdrop" @click.self="ativarAberto = false">
      <div class="modal-card soc-modal">
        <h4>Ativar modo SOC</h4>
        <label>Nova chave de emergência *</label>
        <input v-model="chave" type="password" autocomplete="new-password" />
        <label class="mt-2">Confirmar chave *</label>
        <input v-model="chave2" type="password" autocomplete="new-password" />
        <label class="mt-2">Motivo</label>
        <input v-model="motivo" type="text" placeholder="Ex.: intrusão detectada no servidor" />
        <div class="flex gap-2 mt-4">
          <button
            type="button"
            class="btn btn-danger"
            :disabled="processando"
            @click="ativar"
          >
            {{ processando ? 'A processar…' : 'Confirmar ativação' }}
          </button>
          <button type="button" class="btn btn-ghost" @click="ativarAberto = false">Cancelar</button>
        </div>
      </div>
    </div>

    <div v-if="desativarAberto && socAtivo" class="modal-backdrop" @click.self="desativarAberto = false">
      <div class="modal-card soc-modal">
        <h4>Desativar modo SOC</h4>
        <p class="text-muted" style="font-size: 0.9rem">
          Os dados voltam à criptografia normal do <code>.env</code>. Os envios são liberados.
        </p>
        <label>Chave de emergência usada na ativação *</label>
        <input
          v-model="chaveDesativar"
          type="password"
          autocomplete="off"
          @keyup.enter="desativar"
        />
        <div class="flex gap-2 mt-4">
          <button
            type="button"
            class="btn btn-accent"
            :disabled="processando"
            @click="desativar"
          >
            {{ processando ? 'A processar…' : 'Desativar e restaurar operação' }}
          </button>
          <button type="button" class="btn btn-ghost" @click="desativarAberto = false">
            Cancelar
          </button>
        </div>
      </div>
    </div>
  </section>
</template>

<style scoped>
.soc-painel--ativo {
  border-color: var(--err);
  box-shadow: 0 0 0 1px rgba(197, 48, 48, 0.25);
}
.soc-banner {
  margin-bottom: 0.75rem;
}
.soc-modal {
  max-width: 420px;
}
</style>
