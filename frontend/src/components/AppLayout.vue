<script setup>
import { RouterLink, RouterView, useRouter } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { computed } from 'vue'

const auth = useAuthStore()
const router = useRouter()

const mostrarUsuarios = computed(() => auth.authEnabled)

function sair() {
  auth.logout()
  router.push({ name: 'login' })
}
</script>

<template>
  <div class="app-shell">
    <aside class="app-sidebar">
      <div class="app-brand">
        <h1>Envio de Apólices</h1>
        <small>Painel de Operações</small>
      </div>
      <nav class="sidebar-nav">
        <RouterLink class="nav-link" to="/dashboard">Dashboard</RouterLink>
        <RouterLink class="nav-link" to="/clientes">Clientes</RouterLink>
        <RouterLink class="nav-link" to="/envio">Envio Avulso</RouterLink>
        <RouterLink class="nav-link" to="/historico">Histórico</RouterLink>
        <RouterLink v-if="mostrarUsuarios" class="nav-link" to="/usuarios">Usuários</RouterLink>
      </nav>
      <footer class="sidebar-credit">
        <a
          href="https://www.zontech.online/"
          target="_blank"
          rel="noopener noreferrer"
          title="Zona Tech — zontech.online"
        >
          Zona Tech
        </a>
      </footer>
    </aside>

    <main class="app-main">
      <header class="app-topbar">
        <div>
          <small class="text-muted">
            Autenticação: <strong>{{ auth.authEnabled ? 'ATIVA' : 'DESATIVADA' }}</strong>
          </small>
        </div>
        <div v-if="auth.authEnabled && auth.user">
          <span class="text-muted">{{ auth.user.nome }}</span>
          <button class="btn btn-ghost btn-sm" style="margin-left:.6rem" @click="sair">Sair</button>
        </div>
      </header>

      <RouterView />
    </main>
  </div>
</template>
