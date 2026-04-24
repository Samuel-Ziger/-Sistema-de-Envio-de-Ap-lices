<script setup>
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const router = useRouter()
const route = useRoute()

const username = ref('admin')
const senha = ref('')
const erro = ref('')
const loading = ref(false)

async function entrar() {
  erro.value = ''
  loading.value = true
  try {
    await auth.login(username.value, senha.value)
    router.push(route.query.redirect || '/dashboard')
  } catch (e) {
    erro.value = e.response?.data?.detail || 'Falha no login'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="login-wrap">
    <form class="login-box" @submit.prevent="entrar">
      <h2 style="margin-bottom:.4rem;">Entrar no Sistema</h2>
      <p class="text-muted" style="margin-bottom:1.2rem;">Envio de Apólices — Painel Admin</p>

      <div v-if="erro" class="alert alert-err">{{ erro }}</div>

      <label>Usuário</label>
      <input v-model="username" autocomplete="username" required />

      <label style="margin-top:.8rem;">Senha</label>
      <input v-model="senha" type="password" autocomplete="current-password" required />

      <button class="btn btn-primary" style="margin-top:1.2rem; width:100%;" :disabled="loading">
        {{ loading ? 'Entrando…' : 'Entrar' }}
      </button>

      <p class="text-muted" style="margin-top:1rem; font-size:.8rem;">
        Caso o login esteja desativado, você é direcionado direto ao painel.
      </p>
    </form>
  </div>
</template>
