<template>
  <div v-if="loading" class="flex items-center justify-center h-64">
    <div class="flex flex-col items-center gap-3 text-gray-400">
      <svg class="animate-spin" width="32" height="32" viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="#E5E7EB" stroke-width="3"/>
        <path d="M12 2a10 10 0 0110 10" stroke="#FFCC00" stroke-width="3" stroke-linecap="round"/>
      </svg>
      <p class="text-sm">Chargement…</p>
    </div>
  </div>

  <div v-else-if="importFile" class="space-y-5">

    <!-- File header -->
    <div class="bg-white rounded-2xl border border-border p-5 flex items-center gap-4">
      <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#F5F4EF;border:1px solid #E5E3DB">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="#6E6B63" stroke-width="1.5" stroke-linecap="round"/><polyline points="14 2 14 8 20 8" stroke="#6E6B63" stroke-width="1.5"/></svg>
      </div>
      <div class="flex-1 min-w-0">
        <p class="font-bold truncate" style="color:var(--text-primary);font-family:Montserrat,sans-serif">{{ importFile.original_filename }}</p>
        <p class="text-xs mt-0.5" style="color:var(--text-secondary)">
          {{ importFile.total_rows?.toLocaleString('fr-FR') }} réponses
          <span v-if="importFile.is_surveymonkey"> · fichier reconnu et préparé automatiquement</span>
        </p>
      </div>
      <StatusBadge :status="importFile.status" />
    </div>

    <!-- Success card (post-cleaning) -->
    <div v-if="cleaned" class="bg-white rounded-2xl border border-border p-6">
      <div class="flex items-center gap-4">
        <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#23221E">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><polyline points="20 6 9 17 4 12" stroke="#FFCC00" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        </div>
        <div class="flex-1">
          <p class="font-bold text-base" style="color:var(--text-primary);font-family:Montserrat,sans-serif">Votre fichier est prêt</p>
          <p class="text-sm" style="color:var(--text-secondary)">{{ importFile.total_rows?.toLocaleString('fr-FR') }} réponses nettoyées. Que voulez-vous faire ?</p>
        </div>
      </div>
      <div class="flex flex-wrap gap-3 mt-5">
        <ExportButton :file-id="id" mode="cleaned" format="xlsx" label="Télécharger (Excel)" primary />
        <ExportButton :file-id="id" mode="cleaned" format="csv" label="Télécharger (CSV)" />
        <router-link :to="`/import/${id}/join`"
          class="px-4 py-2 rounded-lg text-sm font-semibold flex items-center gap-2 transition-all"
          style="background:white;color:var(--text-primary);border:1px solid var(--border)">
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          Ajouter les infos clients
        </router-link>
      </div>
    </div>

    <!-- Tableau de bord NPS (post-cleaning) -->
    <div v-if="cleaned && npsMetrics.length" class="bg-white rounded-2xl border border-border p-6">
      <div class="flex items-center justify-between mb-4">
        <div>
          <h3 class="font-bold text-base" style="color:var(--text-primary);font-family:Montserrat,sans-serif">Satisfaction client (NPS), calculée pour vous</h3>
          <p class="text-xs mt-0.5" style="color:var(--text-muted)">
            Les clients qui notent 9-10 sont contents (promoteurs), 0-6 sont mécontents (détracteurs). Le NPS, c'est la différence : au-dessus de 0 c'est bien, au-dessus de +50 c'est excellent.
          </p>
        </div>
        <div v-if="npsMetrics.length > 1" class="text-right">
          <p class="text-2xl font-black" :style="`color:${globalNpsColor};font-family:Montserrat,sans-serif`">
            {{ globalNps > 0 ? '+' : '' }}{{ globalNps }}
          </p>
          <p class="text-xs" style="color:var(--text-muted)">NPS global</p>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <NpsCard v-for="m in npsMetrics" :key="m.column" :metric="m" />
      </div>
    </div>

    <!-- Alerte doublons (post-cleaning) -->
    <div v-if="cleaned && Object.keys(duplicates).length" class="rounded-2xl p-5"
      style="background:#FFFBEB;border:1px solid #FDE68A">
      <div class="flex items-start gap-3">
        <svg class="flex-shrink-0 mt-0.5" width="18" height="18" viewBox="0 0 24 24" fill="none"><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="#B7791F" stroke-width="2"/><line x1="12" y1="9" x2="12" y2="13" stroke="#B7791F" stroke-width="2" stroke-linecap="round"/><line x1="12" y1="17" x2="12.01" y2="17" stroke="#B7791F" stroke-width="2.5" stroke-linecap="round"/></svg>
        <div class="flex-1">
          <p class="font-bold text-sm" style="color:#92400E;font-family:Montserrat,sans-serif">Des clients ont peut-être répondu plusieurs fois</p>
          <div v-for="(info, col) in duplicates" :key="col" class="text-xs mt-1.5" style="color:#92400E">
            {{ info.duplicate_rows }} réponse(s) viennent d'un numéro déjà présent
            <template v-if="info.examples.length">— par exemple
              <span v-for="ex in info.examples" :key="ex.value" class="inline-block px-1.5 py-0.5 rounded ml-1"
                style="background:white;border:1px solid #FDE68A">le {{ ex.value }} a répondu {{ ex.count }} fois</span>
            </template>
          </div>
          <p class="text-xs mt-2" style="color:#B7791F">Ce n'est pas forcément une erreur : un client a pu répondre deux fois. Jetez-y un œil avant de présenter les chiffres.</p>
        </div>
      </div>
    </div>

    <!-- Column naming -->
    <div class="bg-white rounded-2xl border border-border overflow-hidden">
      <div class="px-5 py-4 border-b border-border">
        <h3 class="font-black text-gray-800" style="font-family:Montserrat,sans-serif">Nommez vos colonnes</h3>
        <p class="text-xs text-gray-500 mt-1">
          Donnez un nom court à chaque colonne (ex : « NPS_agent », « Verbatims »). Décochez celles que vous ne voulez pas garder.
        </p>
      </div>

      <div class="divide-y divide-gray-50">
        <div v-for="col in visibleColumns" :key="col.index"
          class="flex items-center gap-4 px-5 py-3 col-row"
          :class="{
            'opacity-40': dropped.has(col.original_name),
            'is-dragging': dragIndex === col.index,
            'drop-above': dragOverIndex === col.index && dragIndex !== col.index,
          }"
          :draggable="grabbed === col.index"
          @dragstart="onDragStart(col, $event)"
          @dragend="onDragEnd"
          @dragover.prevent="onDragOver(col)"
          @drop="onDrop(col)">

          <!-- Drag handle -->
          <div class="drag-handle" title="Glisser pour réordonner"
            @mousedown="grabbed = col.index" @mouseup="grabbed = null">
            <svg width="11" height="16" viewBox="0 0 16 24" fill="currentColor">
              <circle cx="5" cy="5" r="1.6"/><circle cx="11" cy="5" r="1.6"/>
              <circle cx="5" cy="12" r="1.6"/><circle cx="11" cy="12" r="1.6"/>
              <circle cx="5" cy="19" r="1.6"/><circle cx="11" cy="19" r="1.6"/>
            </svg>
          </div>

          <!-- Keep checkbox -->
          <button @click="toggleDrop(col.original_name)"
            class="w-5 h-5 rounded flex items-center justify-center flex-shrink-0 transition-all"
            :style="dropped.has(col.original_name) ? 'border:1.5px solid #D5D2C8;background:white' : 'background:#23221E;border:1.5px solid #23221E'">
            <svg v-if="!dropped.has(col.original_name)" width="10" height="10" viewBox="0 0 24 24" fill="none"><polyline points="20 6 9 17 4 12" stroke="#FFCC00" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </button>

          <!-- Original question -->
          <div class="flex-1 min-w-0">
            <p class="text-sm truncate" style="color:var(--text-primary)" :title="col.original_name">{{ col.original_name }}</p>
            <p v-if="col.is_multi" class="text-xs" style="color:var(--text-muted)">Question à choix multiples — les réponses seront regroupées</p>
            <p v-if="col.is_join_key" class="text-xs font-semibold inline-flex items-center gap-1" style="color:var(--text-secondary)">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
              Numéro de ticket — servira à relier les infos clients
            </p>
          </div>

          <!-- Arrow -->
          <svg class="flex-shrink-0" style="color:#D5D2C8" width="16" height="16" viewBox="0 0 24 24" fill="none"><line x1="5" y1="12" x2="19" y2="12" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><polyline points="12 5 19 12 12 19" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>

          <!-- Target name input -->
          <input
            v-model="mapping[col.original_name]"
            :disabled="dropped.has(col.original_name)"
            :placeholder="col.original_name"
            class="w-56 px-3 py-2 rounded-lg text-sm font-medium transition-all"
            :style="col.is_join_key
              ? 'border:1.5px solid #23221E;background:#FAF9F5;font-family:Montserrat,sans-serif;outline:none'
              : 'border:1px solid var(--border);font-family:Montserrat,sans-serif;outline:none'" />
        </div>
      </div>

      <!-- Hidden technical columns -->
      <div v-if="technicalColumns.length" class="px-5 py-3 border-t border-gray-100 bg-gray-50">
        <button @click="showTechnical = !showTechnical" class="text-xs text-gray-500 hover:text-gray-700 font-medium">
          {{ showTechnical ? '▾' : '▸' }} {{ technicalColumns.length }} colonnes vides ignorées (email, prénom…) — cliquer pour {{ showTechnical ? 'masquer' : 'voir' }}
        </button>
        <div v-if="showTechnical" class="mt-2 space-y-1">
          <div v-for="col in technicalColumns" :key="col.index" class="flex items-center gap-3 text-xs text-gray-400">
            <button @click="toggleDrop(col.original_name)"
              class="w-5 h-5 rounded flex items-center justify-center border-2 transition-all"
              :style="dropped.has(col.original_name) ? 'border:1.5px solid #D5D2C8;background:white' : 'background:#23221E;border:1.5px solid #23221E'">
              <svg v-if="!dropped.has(col.original_name)" width="10" height="10" viewBox="0 0 24 24" fill="none"><polyline points="20 6 9 17 4 12" stroke="#FFCC00" stroke-width="3.5" stroke-linecap="round"/></svg>
            </button>
            {{ col.original_name }}
          </div>
        </div>
      </div>
    </div>

    <!-- Validate bar -->
    <div v-if="!cleaned" class="bg-white rounded-2xl border border-border p-5">
      <div class="flex items-end gap-3 flex-wrap">
        <div class="flex-1 min-w-[220px]">
          <label class="block text-xs font-bold text-gray-500 mb-1.5">
            Nom de ce format (pour le réutiliser la prochaine fois)
          </label>
          <input v-model="templateName" class="input-base" placeholder="ex : VOC EBU" />
        </div>
        <button @click="applyCleaning" :disabled="cleaning"
          class="btn-primary flex items-center gap-2 px-8 py-3 text-base">
          <svg v-if="cleaning" class="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="rgba(0,0,0,.2)" stroke-width="3"/>
            <path d="M12 2a10 10 0 0110 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
          </svg>
          {{ cleaning ? 'Un instant…' : 'Valider ✓' }}
        </button>
      </div>
    </div>

    <!-- Valeurs manquantes (post-cleaning) -->
    <div v-if="cleaned && Object.keys(missingReport).length" class="bg-white rounded-2xl border border-border p-5">
      <h3 class="font-bold text-sm mb-1" style="color:var(--text-primary);font-family:Montserrat,sans-serif">
        Réponses laissées vides
      </h3>
      <p class="text-xs mb-3" style="color:var(--text-muted)">Pour info — c'est souvent normal (toutes les questions ne s'affichent pas à tout le monde).</p>
      <div class="grid grid-cols-2 sm:grid-cols-4 gap-2">
        <div v-for="(info, col) in missingReport" :key="col"
          class="p-2.5 rounded-lg" style="background:#FAF9F5;border:1px solid var(--border)">
          <p class="text-xs font-semibold truncate" style="color:var(--text-primary)" :title="col">{{ col }}</p>
          <p class="text-xs mt-0.5" style="color:var(--text-secondary)">{{ info.missing_count }} vide(s) · {{ info.missing_pct }}%</p>
          <div class="mt-1.5 h-1 rounded-full" style="background:#EFEDE6">
            <div class="h-1 rounded-full" :style="`width:${info.missing_pct}%;background:#9C998F`"></div>
          </div>
        </div>
      </div>
    </div>

    <!-- Preview (post-cleaning) -->
    <div v-if="cleaned && preview.length" class="bg-white rounded-2xl border border-border overflow-hidden">
      <div class="px-5 py-4 border-b border-border">
        <h3 class="font-black text-gray-800" style="font-family:Montserrat,sans-serif">Aperçu du résultat</h3>
      </div>
      <div class="overflow-x-auto">
        <table class="text-xs w-full">
          <thead class="bg-gray-50">
            <tr>
              <th v-for="col in previewCols" :key="col"
                class="px-3 py-2 text-left font-bold text-gray-600 whitespace-nowrap border-b border-gray-100"
                :style="col === joinKeyFinal ? 'background:#F5F4EF;color:#21201C' : ''">
                {{ col }}
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-50">
            <tr v-for="(row, i) in preview" :key="i" class="hover:bg-gray-50">
              <td v-for="col in previewCols" :key="col"
                class="px-3 py-1.5 text-gray-600 max-w-[200px] truncate whitespace-nowrap"
                :title="row[col]">
                {{ row[col] || '—' }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import api from '@/composables/useApi'
import StatusBadge from '@/components/StatusBadge.vue'
import ExportButton from '@/components/ExportButton.vue'
import NpsCard from '@/components/NpsCard.vue'

const route = useRoute()
const toast = useToast()
const id = route.params.id

const loading = ref(true)
const cleaning = ref(false)
const cleaned = ref(false)
const importFile = ref(null)
const structure = ref(null)
const columns = ref([])
const mapping = ref({})
const dropped = ref(new Set())
const headerSkip = ref(2)
const preview = ref([])
const previewCols = ref([])
const missingReport = ref({})
const npsMetrics = ref([])
const duplicates = ref({})
const joinKeyFinal = ref('')
const templateName = ref('')
const showTechnical = ref(false)
const grabbed = ref(null)
const dragIndex = ref(null)
const dragOverIndex = ref(null)

const globalNps = computed(() =>
  npsMetrics.value.length
    ? Math.round(npsMetrics.value.reduce((a, m) => a + m.nps, 0) / npsMetrics.value.length * 10) / 10
    : 0
)
const globalNpsColor = computed(() =>
  globalNps.value >= 50 ? '#21A05A' : globalNps.value >= 0 ? '#B7791F' : '#D4452C'
)

// Colonnes vides à masquer par défaut (email, prénom… toujours vides dans SurveyMonkey)
const TECHNICAL = ['email_address', 'first_name', 'last_name', 'custom_1']

const technicalColumns = computed(() =>
  columns.value.filter(c => TECHNICAL.includes(c.raw_name?.toLowerCase?.() || c.original_name.toLowerCase()))
)
const visibleColumns = computed(() =>
  columns.value.filter(c => !TECHNICAL.includes(c.raw_name?.toLowerCase?.() || c.original_name.toLowerCase()))
)

function toggleDrop(name) {
  const s = new Set(dropped.value)
  if (s.has(name)) s.delete(name)
  else s.add(name)
  dropped.value = s
}

// Réordonner une colonne (monter/descendre) parmi les colonnes visibles
// Réordonnancement par glisser-déposer
function onDragStart(col, e) {
  if (grabbed.value !== col.index) { e.preventDefault(); return }
  dragIndex.value = col.index
  e.dataTransfer.effectAllowed = 'move'
}
function onDragOver(col) {
  if (dragIndex.value !== null) dragOverIndex.value = col.index
}
function onDrop(target) {
  if (dragIndex.value === null || dragIndex.value === target.index) return
  const arr = [...columns.value]
  const from = arr.findIndex(c => c.index === dragIndex.value)
  const to = arr.findIndex(c => c.index === target.index)
  const [moved] = arr.splice(from, 1)
  arr.splice(to, 0, moved)
  columns.value = arr
}
function onDragEnd() {
  dragIndex.value = null
  dragOverIndex.value = null
  grabbed.value = null
}

async function applyCleaning() {
  cleaning.value = true
  try {
    // Ordre final = ordre d'affichage des colonnes conservées (noms cibles)
    const columnOrder = columns.value
      .filter(c => !dropped.value.has(c.original_name))
      .map(c => (mapping.value[c.original_name] || c.original_name).trim())

    const { data } = await api.post(`/imports/files/${id}/apply_cleaning/`, {
      column_mapping: mapping.value,
      columns_to_drop: [...dropped.value],
      header_rows_to_skip: headerSkip.value,
      column_order: columnOrder,
      save_template: true,
      template_name: templateName.value || `Modèle ${importFile.value.survey_type || 'Enquête'}`,
    })
    preview.value = data.preview
    previewCols.value = data.columns
    missingReport.value = data.missing_report || {}
    npsMetrics.value = data.nps_metrics || []
    duplicates.value = data.duplicates || {}
    joinKeyFinal.value = data.join_key || ''
    cleaned.value = true
    importFile.value.status = 'CLEANED'
    importFile.value.total_rows = data.rows
    window.scrollTo({ top: 0, behavior: 'smooth' })
  } catch (e) {
    const err = e.response?.data?.error || 'Une erreur est survenue, réessayez.'
    toast.add({ severity: 'error', summary: 'Oups', detail: err, life: 8000 })
    console.error(e.response?.data?.detail || err)
  } finally {
    cleaning.value = false
  }
}

onMounted(async () => {
  try {
    const { data } = await api.get(`/imports/files/${id}/`)
    importFile.value = data
    structure.value = data.detected_structure || {}
    columns.value = structure.value.detected_columns || []
    headerSkip.value = data.header_rows_to_skip || 2
    templateName.value = data.survey_type || ''

    const m = {}
    columns.value.forEach(c => {
      const saved = data.column_mapping?.[c.original_name]
      m[c.original_name] = saved || c.suggested_name || c.original_name
    })
    mapping.value = m
    dropped.value = new Set(data.columns_to_drop || [])

    if (['CLEANED', 'JOINED'].includes(data.status)) {
      cleaned.value = true
      previewCols.value = structure.value.cleaned_columns || []
      missingReport.value = structure.value.missing_values_report || {}
      npsMetrics.value = structure.value.nps_metrics || []
      duplicates.value = structure.value.duplicates || {}
      joinKeyFinal.value = structure.value.join_key_final || ''
    }
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.col-row { transition: background-color 0.15s ease, box-shadow 0.15s ease; }
.col-row:hover:not(.is-dragging) { background: #FAF9F5; }

.drag-handle {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 24px;
  color: #C9C6BC;
  cursor: grab;
  border-radius: 4px;
  transition: color 0.15s ease, background-color 0.15s ease;
}
.drag-handle:hover { color: #21201C; background: #F0EEE7; }
.drag-handle:active { cursor: grabbing; }

/* Ligne en cours de déplacement */
.is-dragging {
  opacity: 0.5;
  background: #FFFBEB !important;
}
/* Indicateur de la position de dépôt */
.drop-above {
  box-shadow: inset 0 2px 0 0 #FFCC00;
}
</style>
