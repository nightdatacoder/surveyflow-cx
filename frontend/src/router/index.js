import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  { path: '/login', component: () => import('@/views/LoginView.vue'), meta: { guest: true } },
  {
    path: '/',
    component: () => import('@/layouts/AppLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      { path: '', redirect: '/dashboard' },
      { path: 'dashboard', component: () => import('@/views/DashboardView.vue') },
      { path: 'import', component: () => import('@/views/ImportView.vue') },
      { path: 'import/:id/configure', component: () => import('@/views/ConfigureView.vue') },
      { path: 'import/:id/join', component: () => import('@/views/JoinView.vue') },
      { path: 'history', component: () => import('@/views/HistoryView.vue') },
      { path: 'templates', component: () => import('@/views/TemplatesView.vue') },
      { path: 'users', component: () => import('@/views/UsersView.vue'), meta: { role: 'ADMIN' } },
      { path: 'logs', component: () => import('@/views/LogsView.vue'), meta: { role: 'ADMIN' } },
    ]
  },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const auth = useAuthStore()
  if (to.meta.requiresAuth && !auth.token) return next('/login')
  if (to.meta.guest && auth.token) return next('/')
  if (to.meta.role && auth.user?.role !== to.meta.role && auth.user?.role !== 'ADMIN') return next('/')
  next()
})

export default router
