<template>
  <div class="space-y-4">
    <h2 class="font-semibold text-gray-700">Journal d'activité</h2>
    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
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
          <tr v-if="!logs.length">
            <td colspan="4" class="px-4 py-10 text-center text-gray-400">Aucune activité</td>
          </tr>
          <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50">
            <td class="px-4 py-2.5 text-xs text-gray-500 whitespace-nowrap">
              {{ formatDateTime(log.created_at) }}
            </td>
            <td class="px-4 py-2.5">
              <span class="font-medium text-gray-700">{{ log.user_name || 'Système' }}</span>
            </td>
            <td class="px-4 py-2.5">
              <span class="px-2 py-0.5 rounded text-xs font-semibold" :style="actionStyle(log.action)">
                {{ log.action_label }}
              </span>
            </td>
            <td class="px-4 py-2.5 text-gray-500 text-xs">{{ log.description }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/useApi'

const logs = ref([])

function formatDateTime(d) {
  return new Date(d).toLocaleString('fr-FR', { day:'2-digit', month:'2-digit', year:'numeric', hour:'2-digit', minute:'2-digit' })
}

const ACTION_STYLES = {
  IMPORT: 'background:#dbeafe;color:#1d4ed8',
  CLEAN: 'background:#dcfce7;color:#166534',
  JOIN: 'background:#F5F4EF;color:#21201C',
  EXPORT: 'background:#fef9c3;color:#854d0e',
  LOGIN: 'background:#e0f2fe;color:#0369a1',
  LOGOUT: 'background:#f1f5f9;color:#475569',
  CREATE_USER: 'background:#FFCC0040;color:#854d0e',
  DELETE: 'background:#fee2e2;color:#991b1b',
}

function actionStyle(action) { return ACTION_STYLES[action] || 'background:#f1f5f9;color:#475569' }

onMounted(async () => {
  const { data } = await api.get('/history/logs/').catch(() => ({ data: [] }))
  logs.value = data.results || data
})
</script>
