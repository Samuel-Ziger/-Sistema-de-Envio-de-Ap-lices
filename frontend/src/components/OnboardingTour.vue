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
    texto:
      'Este sistema envia apólices por e-mail no modo automático (FULL) ou manual. O tour mostra o essencial — incluindo como montar os e-mails com atalhos e HTML.',
    rota: '/dashboard',
    largo: false,
  },
  {
    titulo: 'Dashboard e modo FULL',
    texto: 'Acompanhe estatísticas, alertas do FULL e o interruptor do envio automático.',
    rota: '/dashboard',
    dicas: [
      'Defina o horário de execução do FULL no cartão abaixo dos indicadores.',
      'Os alertas do FULL aparecem aqui quando um PDF não puder ser processado.',
    ],
  },
  {
    titulo: 'Envio manual e modelos de PDF',
    texto:
      'Em Envio Manual, escolha o modelo (Tokio Auto/Moto, Yelum, PDF com senha, etc.). O sistema analisa o PDF e sugere cliente e apólice.',
    rota: '/envio',
    dicas: [
      'PDF protegido: informe a senha no campo amarelo antes de analisar.',
      'O Tutorial no menu lista todos os layouts suportados.',
    ],
  },
  {
    titulo: 'Corpos de e-mail — visão geral',
    texto:
      'Cada tipo de envio (auto, moto, residencial…) pode ter um HTML próprio. O painel Corpos de E-mail é onde você monta esse texto.',
    rota: '/corpos-email',
    dicas: [
      'Cadastre um corpo com nome claro (ex.: «Tokio Auto — padrão 2026»).',
      'Depois associe o corpo ao tipo em Tipos de Envio — assim o FULL usa o HTML certo.',
    ],
  },
  {
    titulo: 'Atalhos: variáveis automáticas',
    texto:
      'Ative «Atalhos visíveis» no editor. Na aba Variáveis, cada botão insere um campo que o sistema preenche no envio.',
    rota: '/corpos-email',
    largo: true,
    dicas: [
      'Formato: chaves duplas com o nome do campo (veja exemplos abaixo).',
      'Exemplos úteis: nome do cliente, número da apólice, placa, remetente.',
      'Clique no botão — o texto é inserido onde estiver o cursor no campo HTML.',
    ],
    exemplos: [
      {
        titulo: 'Variável simples',
        codigo: '<p>Prezado(a) <strong>{{ nome }}</strong>,</p>',
      },
      {
        titulo: 'Apólice opcional (só aparece se existir)',
        codigo:
          '{% if numero_apolice %}Apólice nº <strong>{{ numero_apolice }}</strong>{% endif %}',
      },
    ],
  },
  {
    titulo: 'Atalhos: blocos por modelo de apólice',
    texto:
      'Na aba «Por modelo», use «Inserir bloco» para colar um e-mail já adaptado ao layout (Tokio, Yelum, manual…).',
    rota: '/corpos-email',
    dicas: [
      'Ajuste o texto depois de inserir — o bloco é ponto de partida, não regra fixa.',
      'Badges FULL / Manual indicam se o layout costuma rodar na pasta automática.',
      'Mantenha as variáveis e os trechos {% if … %} — o sistema usa Jinja2 para montar o e-mail.',
    ],
  },
  {
    titulo: 'Atalhos: criar os seus (equipa)',
    texto:
      'Na aba «Meus atalhos», crie trechos HTML reutilizáveis (rodapé, aviso LGPD, texto da corretora…).',
    rota: '/corpos-email',
    largo: true,
    dicas: [
      'Preencha Nome e HTML, clique «Guardar atalho» — fica disponível para toda a equipa.',
      'Use nomes descritivos: «Rodapé padrão», «Aviso sinistro 0800», etc.',
      'Para inserir num corpo: clique no nome do atalho com o cursor no editor HTML.',
      'Evite colar direto do Word — traz formatação estranha e aspas curvas que quebram o HTML.',
    ],
  },
  {
    titulo: 'Mini-aula: HTML para e-mail',
    texto:
      'O corpo do e-mail é HTML simples (não é página web completa). Algumas tags bastam para um texto profissional.',
    rota: '/corpos-email',
    largo: true,
    aula: true,
    dicas: [
      'Parágrafo: tag p de abertura e fechamento — um por ideia.',
      'Destaque: tag strong para nome ou número da apólice.',
      'Quebra de linha na assinatura: tag br (auto-fechada).',
      'Não use html, head ou body — o sistema já envolve o seu conteúdo.',
    ],
    exemplos: [
      {
        titulo: 'Estrutura mínima recomendada',
        codigo: `<p>Prezado(a) <strong>{{ nome }}</strong>,</p>
<p>Segue em anexo sua apólice{% if numero_apolice %} nº <strong>{{ numero_apolice }}</strong>{% endif %}.</p>
<p>Atenciosamente,<br/>{{ from_name }}</p>`,
      },
      {
        titulo: 'Destaque opcional (caixa colorida)',
        codigo: `<div style="margin:1em 0;padding:.85em 1em;background:#f7faf9;border-left:3px solid #00B94E;">
  Texto fixo ou variável {{ nome }} conforme o seu modelo.
</div>`,
      },
    ],
    avisos: [
      'Feche todas as tags (cada p precisa de fechamento).',
      'Não apague {% if %} nem {% endif %} — são condicionais do sistema.',
      'Use aspas retas do teclado — evite aspas tipográficas do Word.',
    ],
  },
  {
    titulo: 'Ligar corpo ao tipo de envio',
    texto:
      'Um corpo bonito só entra em ação quando está ligado ao tipo certo — senão o sistema usa o template padrão.',
    rota: '/tipos-envio',
    dicas: [
      'Em Tipos de Envio, edite o tipo (auto, moto…) e escolha o Corpo de e-mail.',
      'O código do tipo deve bater com a pasta do FULL (ex.: pasta entrada/auto/).',
    ],
  },
  {
    titulo: 'Tutorial e histórico',
    texto:
      'Consulte o Tutorial para tabelas de modelos, PDF com senha e auditoria. O Histórico regista quem enviou e quem colocou ficheiros no FULL.',
    rota: '/tutorial',
    dicas: ['Pode rever este tour a qualquer momento: «Rever tour guiado» no menu.'],
  },
]

const atual = computed(() => passos[passo.value])
const ultimo = computed(() => passo.value >= passos.length - 1)
const cardLargo = computed(() => atual.value?.largo || atual.value?.aula)

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

function anterior() {
  if (passo.value > 0) {
    passo.value -= 1
    irParaPasso()
  }
}

function pular() {
  ui.marcarTourConcluido()
  emit('fechar')
}

onMounted(irParaPasso)
</script>

<template>
  <div class="tour-overlay" role="dialog" aria-modal="true" aria-labelledby="tour-titulo">
    <div class="tour-card" :class="{ 'tour-card--largo': cardLargo }">
      <p class="tour-step-label">Passo {{ passo + 1 }} de {{ passos.length }}</p>
      <h3 id="tour-titulo">{{ atual.titulo }}</h3>
      <div class="tour-body">
        <p class="tour-lead">{{ atual.texto }}</p>

        <ul v-if="atual.dicas?.length" class="tour-lista">
          <li v-for="(d, i) in atual.dicas" :key="i">{{ d }}</li>
        </ul>

        <div v-if="atual.exemplos?.length" class="tour-exemplos">
          <div v-for="(ex, i) in atual.exemplos" :key="i" class="tour-exemplo">
            <p class="tour-exemplo-titulo">{{ ex.titulo }}</p>
            <pre class="tour-code"><code>{{ ex.codigo }}</code></pre>
          </div>
        </div>

        <ul v-if="atual.avisos?.length" class="tour-avisos">
          <li v-for="(a, i) in atual.avisos" :key="'a' + i">{{ a }}</li>
        </ul>

        <p v-if="atual.aula" class="tour-nota text-muted">
          Variáveis <code v-pre>{{ nome }}</code> são trocadas no envio. Trechos
          <code v-pre>{% if … %}</code> mostram ou escondem partes conforme os dados do PDF.
        </p>
      </div>

      <div class="tour-dots" aria-hidden="true">
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
        <button v-if="passo > 0" type="button" class="btn btn-ghost" @click="anterior">
          Anterior
        </button>
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
  max-height: min(90vh, 720px);
  display: flex;
  flex-direction: column;
  box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
}
.tour-card--largo {
  max-width: 560px;
}
.tour-body {
  overflow-y: auto;
  flex: 1;
  min-height: 0;
  margin-bottom: 0.5rem;
  padding-right: 0.25rem;
}
.tour-step-label {
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--accent-2);
  margin: 0 0 0.5rem;
  font-weight: 700;
}
.tour-lead {
  margin: 0 0 0.75rem;
  color: var(--text);
  line-height: 1.5;
  font-size: 0.95rem;
}
.tour-lista {
  margin: 0 0 0.75rem;
  padding-left: 1.2rem;
  font-size: 0.9rem;
  line-height: 1.55;
  color: var(--muted);
}
.tour-exemplos {
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  margin-bottom: 0.75rem;
}
.tour-exemplo-titulo {
  margin: 0 0 0.25rem;
  font-size: 0.82rem;
  font-weight: 600;
  color: var(--accent-2);
}
.tour-code {
  margin: 0;
  padding: 0.65rem 0.75rem;
  background: #1e1e1e;
  color: #e8e6e3;
  border-radius: 8px;
  font-size: 0.72rem;
  line-height: 1.45;
  overflow-x: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
.tour-avisos {
  margin: 0 0 0.5rem;
  padding: 0.65rem 0.85rem 0.65rem 1.1rem;
  background: rgba(197, 48, 48, 0.08);
  border-left: 3px solid var(--err);
  font-size: 0.85rem;
  line-height: 1.5;
}
.tour-nota {
  font-size: 0.82rem;
  margin: 0.5rem 0 0;
  line-height: 1.45;
}
.tour-dots {
  display: flex;
  gap: 0.35rem;
  margin: 0.75rem 0;
  flex-shrink: 0;
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
  flex-shrink: 0;
}
</style>
