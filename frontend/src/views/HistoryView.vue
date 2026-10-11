<template>
  <div class="space-y-4">
    <!-- En-tête -->
    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
      <h2 class="font-bold text-lg" style="color:#21201C;font-family:Montserrat,sans-serif">Mes traitements</h2>
      <div class="flex items-center gap-2">
        <select v-model="filterType" class="flex-1 sm:flex-none px-3 py-2 border border-gray-200 rounded-lg text-sm bg-white">
          <option value="">Toutes les enquêtes</option>
          <option v-for="t in surveyTypes" :key="t" :value="t">{{ t }}</option>
        </select>
        <button @click="exportBacklog" :disabled="!filterType"
          class="px-3 py-2 rounded-lg text-sm font-semibold disabled:opacity-40 whitespace-nowrap flex items-center gap-1.5"
          style="background:#FFCC00;color:#23221E"
          :title="filterType ? `Réunir tous vos fichiers ${filterType} en un seul Excel` : 'Choisissez d\'abord une enquête'">
          <i class="pi pi-download"></i><span class="hidden sm:inline">Tout réunir</span>
        </button>
      </div>
    </div>

    <!-- Loader -->
    <div v-if="loading" class="bg-white rounded-xl p-12 flex justify-center" style="border:1px solid var(--border)">
      <Spinner label="Chargement de l'historique…" />
    </div>

    <template v-else>
      <!-- Vide -->
      <div v-if="!filteredReports.length" class="bg-white rounded-xl p-12 text-center" style="border:1px solid var(--border);color:#9C998F">
        <i class="pi pi-inbox text-3xl block mb-2"></i>Aucun traitement pour l'instant
      </div>

      <!-- Tableau (desktop) -->
      <div v-else class="bg-white rounded-xl overflow-hidden hidden md:block" style="border:1px solid var(--border)">
        <table class="w-full text-sm">
          <thead class="bg-gray-50">
            <tr class="text-left text-xs text-gray-500">
              <th class="px-4 py-3 font-semibold">Projet</th>
              <th class="px-4 py-3 font-semibold">Type</th>
              <th class="px-4 py-3 font-semibold">Par</th>
              <th class="px-4 py-3 font-semibold">Lignes</th>
              <th class="px-4 py-3 font-semibold">Enrichi</th>
              <th class="px-4 py-3 font-semibold">Date et heure</th>
              <th class="px-4 py-3"></th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="r in filteredReports" :key="r.id" class="hover:bg-gray-50">
              <td class="px-4 py-3 font-medium text-gray-700 max-w-[220px] truncate" :title="r.project_name">{{ r.project_name }}</td>
              <td class="px-4 py-3"><span class="px-2 py-0.5 text-xs rounded-md font-semibold whitespace-nowrap" style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB">{{ r.survey_type }}</span></td>
              <td class="px-4 py-3">
                <div class="flex items-center gap-2">
                  <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0" style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB;font-size:9px">{{ initials(r.user_name) }}</div>
                  <span class="text-xs text-gray-600 whitespace-nowrap">{{ r.user_name || '—' }}</span>
                </div>
              </td>
              <td class="px-4 py-3 text-gray-600">{{ r.rows_processed?.toLocaleString('fr-FR') }}</td>
              <td class="px-4 py-3"><i :class="`pi ${r.join_applied ? 'pi-check-circle' : 'pi-minus-circle'}`" :style="r.join_applied ? 'color:#21201C' : 'color:#D5D2C8'"></i></td>
              <td class="px-4 py-3 text-xs whitespace-nowrap"><span class="text-gray-600">{{ formatDate(r.created_at) }}</span> <span class="text-gray-400">{{ formatTime(r.created_at) }}</span></td>
              <td class="px-4 py-3">
                <div v-if="r.import_file" class="flex gap-1.5">
                  <ExportButton :file-id="r.import_file" :mode="r.join_applied ? 'joined' : 'cleaned'" format="xlsx" :label="r.join_applied ? 'Enrichi' : 'Nettoyé'" primary />
                  <ExportButton :file-id="r.import_file" :mode="r.join_applied ? 'joined' : 'cleaned'" format="csv" label="CSV" />
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Cartes (mobile) -->
      <div v-if="filteredReports.length" class="md:hidden space-y-3">
        <div v-for="r in filteredReports" :key="r.id" class="bg-white rounded-xl p-4" style="border:1px solid var(--border)">
          <div class="flex items-start justify-between gap-2 mb-2">
            <p class="font-semibold text-sm text-gray-800 leading-snug" style="word-break:break-word">{{ r.project_name }}</p>
            <span class="px-2 py-0.5 text-xs rounded-md font-semibold whitespace-nowrap flex-shrink-0" style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB">{{ r.survey_type }}</span>
          </div>
          <div class="flex items-center gap-3 text-xs mb-3" style="color:#9C998F">
            <span class="flex items-center gap-1.5">
              <span class="w-5 h-5 rounded-full flex items-center justify-center flex-shrink-0" style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB;font-size:8px">{{ initials(r.user_name) }}</span>
              {{ r.user_name || '—' }}
            </span>
            <span>· {{ r.rows_processed?.toLocaleString('fr-FR') }} lignes</span>
            <span v-if="r.join_applied" style="color:#21A05A">· enrichi</span>
          </div>
          <div class="flex items-center justify-between gap-2">
            <span class="text-xs" style="color:#9C998F">{{ formatDate(r.created_at) }} · {{ formatTime(r.created_at) }}</span>
            <div v-if="r.import_file" class="flex gap-1.5">
              <ExportButton :file-id="r.import_file" :mode="r.join_applied ? 'joined' : 'cleaned'" format="xlsx" :label="r.join_applied ? 'Enrichi' : 'Nettoyé'" primary />
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/useApi'
import ExportButton from '@/components/ExportButton.vue'
import Spinner from '@/components/Spinner.vue'

const reports = ref([])
const filterType = ref('')
const loading = ref(true)

const surveyTypes = computed(() => [...new Set(reports.value.map(r => r.survey_type).filter(Boolean))].sort())
const filteredReports = computed(() => filterType.value ? reports.value.filter(r => r.survey_type === filterType.value) : reports.value)

function initials(name) { return (name || '?').split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase() }
function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR', { day:'2-digit', month:'short', year:'numeric' }) }
function formatTime(d) { return new Date(d).toLocaleTimeString('fr-FR', { hour:'2-digit', minute:'2-digit' }) }

async function exportBacklog() {
  const { data } = await api.post('/exports/backlog/', { survey_type: filterType.value, format: 'xlsx' }, { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([data]))
  const a = document.createElement('a')
  a.href = url; a.download = `backlog_${filterType.value}.xlsx`; a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  try {
    const { data } = await api.get('/history/reports/')
    reports.value = data.results || data
  } catch { reports.value = [] }
  finally { loading.value = false }
})
</script>
