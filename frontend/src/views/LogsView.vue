<template>
  <div class="space-y-4">
    <h2 class="font-bold text-lg" style="color:#21201C;font-family:Montserrat,sans-serif">Journal d'activité</h2>

    <div v-if="loading" class="bg-white rounded-xl p-12 flex justify-center" style="border:1px solid var(--border)">
      <Spinner label="Chargement du journal…" />
    </div>

    <template v-else>
      <div v-if="!logs.length" class="bg-white rounded-xl p-12 text-center" style="border:1px solid var(--border);color:#9C998F">
        <i class="pi pi-inbox text-3xl block mb-2"></i>Aucune activité
      </div>

      <!-- Tableau (desktop) -->
      <div v-else class="bg-white rounded-xl overflow-hidden hidden md:block" style="border:1px solid var(--border)">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr class="text-left text-xs text-gray-500">
              <th class="px-4 py-3 font-semibold">Date / Heure</th>
              <th class="px-4 py-3 font-semibold">Utilisateur</th>
              <th class="px-4 py-3 font-semibold">Action</th>
              <th class="px-4 py-3 font-semibold">Description</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
              <td class="px-4 py-2.5 text-xs text-gray-500 whitespace-nowrap">{{ formatDateTime(log.created_at) }}</td>
              <td class="px-4 py-2.5"><span class="font-medium text-gray-700 whitespace-nowrap">{{ log.user_name || 'Système' }}</span></td>
              <td class="px-4 py-2.5"><span class="px-2 py-0.5 rounded-md text-xs font-semibold whitespace-nowrap inline-flex items-center gap-1.5"><span class="w-1.5 h-1.5 rounded-full" :style="`background:${dot(log.action)}`"></span>{{ log.action_label }}</span></td>
              <td class="px-4 py-2.5 text-gray-500 text-xs">{{ log.description }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Cartes (mobile) -->
      <div class="md:hidden space-y-2.5">
        <div v-for="log in logs" :key="log.id" class="bg-white rounded-xl p-3.5" style="border:1px solid var(--border)">
          <div class="flex items-center justify-between gap-2 mb-1.5">
            <span class="px-2 py-0.5 rounded-md text-xs font-semibold inline-flex items-center gap-1.5" style="background:#F5F4EF;color:#21201C;border:1px solid #E5E3DB">
              <span class="w-1.5 h-1.5 rounded-full" :style="`background:${dot(log.action)}`"></span>{{ log.action_label }}
            </span>
            <span class="text-xs whitespace-nowrap" style="color:#9C998F">{{ formatDateTime(log.created_at) }}</span>
          </div>
          <p class="text-xs text-gray-600 mb-1">{{ log.description }}</p>
          <p class="text-xs" style="color:#9C998F">par {{ log.user_name || 'Système' }}</p>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/useApi'
import Spinner from '@/components/Spinner.vue'

const logs = ref([])
const loading = ref(true)

function formatDateTime(d) {
  return new Date(d).toLocaleString('fr-FR', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })
}

const DOTS = {
  IMPORT: '#2563EB', CLEAN: '#21A05A', JOIN: '#A9790A', EXPORT: '#B7791F',
  LOGIN: '#0EA5E9', LOGOUT: '#9C998F', CREATE_USER: '#A9790A', DELETE: '#D4452C',
}
function dot(action) { return DOTS[action] || '#9C998F' }

onMounted(async () => {
  try {
    const { data } = await api.get('/history/logs/')
    logs.value = data.results || data
  } catch { logs.value = [] }
  finally { loading.value = false }
})
</script>
