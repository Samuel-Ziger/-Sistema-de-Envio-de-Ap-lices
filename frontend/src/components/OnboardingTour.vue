<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useUiStore } from '../stores/ui'

const emit = defineEmits(['fechar'])
const ui = useUiStore()
const router = useRouter()
const passo = ref(0)

const passos = [
  {
    titulo: 'Bem-vindo ao painel Terra Fértil',
    texto: 'Este sistema envia apólices por e-mail no modo automático (FULL) ou manual. Vamos mostrar o essencial em poucos passos.',
    rota: '/dashboard',
  },
  {
    titulo: 'Envio por modelo de apólice',
    texto: 'Em Envio Manual, escolha o modelo (Tokio Auto/Moto, Yelum, PDF protegido ou só imagem). O Tutorial lista todos os layouts suportados.',
    rota: '/envio',
  },
  {
    titulo: 'Envio manual com pré-visualização',
    texto: 'Ao selecionar um PDF, o sistema analisa o layout, sugere CPF/apólice e pode usar OCR em PDFs só imagem (se o Tesseract estiver instalado no servidor).',
    rota: '/envio',
  },
  {
    titulo: 'Alertas do modo FULL',
    texto: 'Quando o FULL não conseguir processar um PDF (cliente não cadastrado, PDF protegido, etc.), aparecerá um aviso no Dashboard para você agir.',
    rota: '/dashboard',
  },
  {
    titulo: 'Tutorial completo',
    texto: 'A qualquer momento, abra o Tutorial no menu para ver tabelas de modelos, pastas do FULL e dúvidas frequentes.',
    rota: '/tutorial',
  },
]

const atual = computed(() => passos[passo.value])
const ultimo = computed(() => passo.value >= passos.length - 1)

function irParaPasso() {
  if (atual.value?.rota) router.push(atual.value.rota)
}

function proximo() {
  if (ultimo.value) {
    ui.marcarTourConcluido()
    emit('fechar')
    return
  }
  passo.value += 1
  irParaPasso()
}

function pular() {
  ui.marcarTourConcluido()
  emit('fechar')
}

onMounted(irParaPasso)
</script>

<template>
  <div class="tour-overlay" role="dialog" aria-modal="true">
    <div class="tour-card">
      <p class="tour-step-label">Passo {{ passo + 1 }} de {{ passos.length }}</p>
      <h3>{{ atual.titulo }}</h3>
      <p class="text-muted">{{ atual.texto }}</p>
      <div class="tour-dots">
        <span
          v-for="(_, i) in passos"
          :key="i"
          class="tour-dot"
          :class="{ active: i === passo }"
        />
      </div>
      <div class="tour-actions">
        <button type="button" class="btn btn-ghost" @click="pular">Pular tour</button>
        <span class="spacer" />
        <button v-if="passo > 0" type="button" class="btn btn-ghost" @click="passo--">Anterior</button>
        <button type="button" class="btn btn-accent" @click="proximo">
          {{ ultimo ? 'Concluir' : 'Próximo' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.tour-overlay {
  position: fixed;
  inset: 0;
  z-index: 9999;
  background: rgba(46, 26, 14, 0.55);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}
.tour-card {
  background: var(--surface);
  border-radius: var(--radius);
  padding: 1.5rem 1.75rem;
  max-width: 480px;
  width: 100%;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
}
.tour-step-label {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent-2);
  margin: 0 0 0.5rem;
  font-weight: 700;
}
.tour-dots {
  display: flex;
  gap: 0.35rem;
  margin: 1rem 0;
}
.tour-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--terra-300);
}
.tour-dot.active {
  background: var(--accent);
  width: 20px;
  border-radius: 4px;
}
.tour-actions {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}
</style>
