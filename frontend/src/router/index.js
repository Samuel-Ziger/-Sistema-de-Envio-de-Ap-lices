import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const routes = [
  { path: '/', redirect: '/dashboard' },
  { path: '/login', name: 'login', component: () => import('../views/Login.vue'), meta: { public: true } },
  {
    path: '/',
    component: () => import('../components/AppLayout.vue'),
    children: [
      { path: 'dashboard', name: 'dashboard', component: () => import('../views/Dashboard.vue') },
      { path: 'clientes', name: 'clientes', component: () => import('../views/Clientes.vue') },
      { path: 'envio',    name: 'envio',    component: () => import('../views/EnvioAvulso.vue') },
      { path: 'historico', name: 'historico', component: () => import('../views/Historico.vue') },
      { path: 'usuarios', name: 'usuarios', component: () => import('../views/Usuarios.vue') },
    ],
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()
  // carrega flag de auth_enabled 1 vez
  if (auth.authEnabled === false && !auth._loaded) {
    try {
      await auth.carregarStatus()
    } catch { /* backend offline: deixa seguir */ }
    auth._loaded = true
  }

  if (to.meta.public) return true
  if (!auth.authEnabled) return true   // login desativado → libera tudo
  if (!auth.token) return { name: 'login', query: { redirect: to.fullPath } }
  return true
})

export default router
