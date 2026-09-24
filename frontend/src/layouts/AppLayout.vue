<template>
  <div class="flex h-screen overflow-hidden" style="background:var(--bg)">
    <!-- Sidebar -->
    <aside class="w-60 flex-shrink-0 flex flex-col py-5" style="background:var(--sidebar-bg)">
      <!-- Logo -->
      <div class="px-5 mb-8">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center font-black text-xs flex-shrink-0"
               style="background:#FFCC00;color:#23221E;font-family:Montserrat,sans-serif">SF</div>
          <div>
            <p class="font-black text-xs tracking-tight leading-none" style="color:#F5F4EF;font-family:Montserrat,sans-serif">SurveyFlow CX</p>
            <p class="mt-0.5" style="font-size:10px;color:var(--sidebar-text)">MTN Customer Experience</p>
          </div>
        </div>
      </div>

      <!-- Nav sections -->
      <div class="flex-1 px-3 space-y-0.5 overflow-y-auto">
        <p class="px-2 mb-2 font-bold" style="font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#7A776E">Principal</p>
        <NavItem to="/dashboard" label="Tableau de bord">
          <template #icon>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><rect x="3" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/><rect x="14" y="3" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/><rect x="3" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/><rect x="14" y="14" width="7" height="7" rx="1.5" stroke="currentColor" stroke-width="2"/></svg>
          </template>
        </NavItem>
        <NavItem to="/import" label="Importer">
          <template #icon>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><polyline points="17 8 12 3 7 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </template>
        </NavItem>
        <NavItem to="/history" label="Historique">
          <template #icon>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><polyline points="12 6 12 12 16 14" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </template>
        </NavItem>
        <NavItem to="/templates" label="Modèles">
          <template #icon>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </template>
        </NavItem>

        <div v-if="auth.isAdmin" class="pt-4 pb-2">
          <p class="px-2 font-bold" style="font-size:10px;letter-spacing:.08em;text-transform:uppercase;color:#7A776E">Administration</p>
        </div>
        <NavItem v-if="auth.isAdmin" to="/users" label="Utilisateurs">
          <template #icon>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><circle cx="9" cy="7" r="4" stroke="currentColor" stroke-width="2"/><path d="M23 21v-2a4 4 0 00-3-3.87M16 3.13a4 4 0 010 7.75" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </template>
        </NavItem>
        <NavItem v-if="auth.isAdmin" to="/logs" label="Journal">
          <template #icon>
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><polyline points="14 2 14 8 20 8" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="16" y1="13" x2="8" y2="13" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="16" y1="17" x2="8" y2="17" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </template>
        </NavItem>
      </div>

      <!-- User section -->
      <div class="mx-3 mt-4 p-3 rounded-xl" style="background:var(--sidebar-active);border:1px solid #38362F">
        <div class="flex items-center gap-2.5">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center font-bold text-xs flex-shrink-0"
               style="background:#FFCC00;color:#23221E;font-family:Montserrat,sans-serif">
            {{ initials }}
          </div>
          <div class="flex-1 min-w-0">
            <p class="font-bold text-xs truncate" style="color:#F5F4EF;font-family:Montserrat,sans-serif">{{ auth.user?.first_name || auth.user?.username }}</p>
            <p class="text-xs truncate" style="color:var(--sidebar-text)">{{ roleLabel }}</p>
          </div>
          <button @click="handleLogout" class="p-1 rounded-lg transition-all" style="color:#7A776E" title="Déconnexion"
            onmouseover="this.style.color='#F5F4EF'" onmouseout="this.style.color='#7A776E'">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><polyline points="16 17 21 12 16 7" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><line x1="21" y1="12" x2="9" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
          </button>
        </div>
      </div>
    </aside>

    <!-- Main content -->
    <div class="flex-1 flex flex-col overflow-hidden">
      <!-- Top bar -->
      <header class="flex-shrink-0 px-7 py-4 flex items-center justify-between" style="background:var(--bg);border-bottom:1px solid var(--border)">
        <div>
          <h1 class="font-black text-base" style="color:var(--text-primary);font-family:Montserrat,sans-serif;letter-spacing:-.02em">{{ pageTitle }}</h1>
        </div>
        <div class="flex items-center gap-3">
          <span class="px-2.5 py-1 rounded-lg text-xs font-bold" :style="roleBadgeStyle">{{ roleLabel }}</span>
        </div>
      </header>

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-7">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import NavItem from '@/components/NavItem.vue'

const auth = useAuthStore()
const route = useRoute()
const router = useRouter()

const initials = computed(() => {
  const u = auth.user
  if (!u) return '?'
  if (u.first_name && u.last_name) return `${u.first_name[0]}${u.last_name[0]}`.toUpperCase()
  return (u.username || '?')[0].toUpperCase()
})
const roleLabel = computed(() => ({ ADMIN: 'Administrateur', MANAGER: 'Manager CX', AGENT: 'Agent CX' }[auth.user?.role] || ''))
const roleBadgeStyle = computed(() => ({
  ADMIN: 'background:#23221E;color:#FFCC00',
  MANAGER: 'background:#F5F4EF;color:#21201C;border:1px solid #E5E3DB',
  AGENT: 'background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB',
}[auth.user?.role] || ''))

const titles = {
  '/dashboard': 'Tableau de bord', '/import': 'Importer', '/history': 'Historique',
  '/templates': 'Modèles', '/users': 'Utilisateurs', '/logs': 'Journal',
}
const pageTitle = computed(() => {
  if (route.path.includes('/configure')) return 'Configurer les colonnes'
  if (route.path.includes('/join')) return 'Ajouter les infos clients'
  return titles[route.path] || 'SurveyFlow CX'
})

async function handleLogout() { await auth.logout(); router.push('/login') }
</script>
