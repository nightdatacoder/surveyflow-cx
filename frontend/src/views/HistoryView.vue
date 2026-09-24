<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="font-semibold text-gray-700">Mes traitements</h2>
      <div class="flex gap-2">
        <select v-model="filterType" class="px-3 py-2 border border-gray-200 rounded-lg text-sm">
          <option value="">Toutes les enquêtes</option>
          <option v-for="t in surveyTypes" :key="t" :value="t">{{ t }}</option>
        </select>
        <button @click="exportBacklog" :disabled="!filterType" class="px-4 py-2 rounded-lg text-sm font-semibold disabled:opacity-40" style="background:#FFCC00;color:#23221E"
          :title="filterType ? `Réunir tous vos fichiers ${filterType} en un seul Excel` : 'Choisissez d\'abord une enquête'">
          <i class="pi pi-download mr-1"></i>Tout réunir{{ filterType ? ' : ' + filterType : '' }}
        </button>
      </div>
    </div>

    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
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
          <tr v-if="!reports.length">
            <td colspan="7" class="px-4 py-10 text-center text-gray-400">Aucun rapport</td>
          </tr>
          <tr v-for="r in filteredReports" :key="r.id" class="hover:bg-gray-50">
            <td class="px-4 py-3 font-medium text-gray-700">{{ r.project_name }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 text-xs rounded-md font-semibold" style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB">{{ r.survey_type }}</span>
            </td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-2">
                <div class="w-6 h-6 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                     style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB;font-size:9px">
                  {{ (r.user_name || '?').split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase() }}
                </div>
                <span class="text-xs text-gray-600">{{ r.user_name || '—' }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-600">{{ r.rows_processed?.toLocaleString() }}</td>
            <td class="px-4 py-3">
              <i :class="`pi ${r.join_applied ? 'pi-check-circle' : 'pi-minus-circle'}`"
                 :style="r.join_applied ? 'color:#21201C' : 'color:#D5D2C8'"></i>
            </td>
            <td class="px-4 py-3 text-xs">
              <span class="text-gray-600">{{ formatDate(r.created_at) }}</span>
              <span class="text-gray-400 ml-1">{{ formatTime(r.created_at) }}</span>
            </td>
            <td class="px-4 py-3">
              <div v-if="r.import_file" class="flex gap-1.5">
                <ExportButton :file-id="r.import_file" :mode="r.join_applied ? 'joined' : 'cleaned'" format="xlsx"
                  :label="r.join_applied ? 'Enrichi XLSX' : 'Nettoyé XLSX'" primary />
                <ExportButton :file-id="r.import_file" :mode="r.join_applied ? 'joined' : 'cleaned'" format="csv" label="CSV" />
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import api from '@/composables/useApi'
import ExportButton from '@/components/ExportButton.vue'

const reports = ref([])
const filterType = ref('')

// Le filtre reflète les types réellement présents dans l'historique
const surveyTypes = computed(() =>
  [...new Set(reports.value.map(r => r.survey_type).filter(Boolean))].sort()
)

const filteredReports = computed(() =>
  filterType.value ? reports.value.filter(r => r.survey_type === filterType.value) : reports.value
)

function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR', { day:'2-digit', month:'short', year:'numeric' }) }
function formatTime(d) { return new Date(d).toLocaleTimeString('fr-FR', { hour:'2-digit', minute:'2-digit' }) }

async function exportBacklog() {
  const { data, headers } = await api.post('/exports/backlog/', { survey_type: filterType.value, format: 'xlsx' }, { responseType: 'blob' })
  const url = URL.createObjectURL(new Blob([data]))
  const a = document.createElement('a')
  a.href = url; a.download = `backlog_${filterType.value}.xlsx`; a.click()
  URL.revokeObjectURL(url)
}

onMounted(async () => {
  const { data } = await api.get('/history/reports/').catch(() => ({ data: [] }))
  reports.value = data.results || data
})
</script>
