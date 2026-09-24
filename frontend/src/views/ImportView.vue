<template>
  <div class="space-y-5">

    <!-- Upload zone -->
    <div class="bg-white rounded-2xl border border-border p-6">
      <h2 class="font-black text-sm uppercase tracking-widest text-gray-400 mb-4" style="font-family:Montserrat,sans-serif">
        Importer un fichier d'enquête
      </h2>

      <!-- Drop zone -->
      <div v-if="!selectedFile"
        @dragover.prevent="dragging = true" @dragleave="dragging = false" @drop.prevent="onDrop"
        @click="$refs.fileInput.click()"
        class="border-2 border-dashed rounded-xl p-10 text-center cursor-pointer transition-all"
        :class="dragging ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'">
        <input ref="fileInput" type="file" accept=".xlsx,.xls,.csv" class="hidden" @change="onFileSelect" />
        <svg class="mx-auto mb-3" :style="`color:${dragging ? '#FFCC00' : '#D1D5DB'}`" width="40" height="40" viewBox="0 0 24 24" fill="none">
          <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
          <polyline points="17 8 12 3 7 8" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/>
          <line x1="12" y1="3" x2="12" y2="15" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/>
        </svg>
        <p class="font-semibold text-gray-600 text-sm">Glissez votre fichier ou cliquez pour parcourir</p>
        <p class="text-xs text-gray-400 mt-1">XLSX · XLS · CSV — Max 50 Mo</p>
      </div>

      <!-- File selected -->
      <div v-else class="flex items-center gap-3 p-4 rounded-xl" style="background:#FAF9F5;border:1px solid var(--border)">
        <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#23221E">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="#FFCC00" stroke-width="2" stroke-linecap="round"/><polyline points="14 2 14 8 20 8" stroke="#FFCC00" stroke-width="2" stroke-linecap="round"/></svg>
        </div>
        <div class="flex-1">
          <p class="font-bold text-sm" style="color:var(--text-primary)">{{ selectedFile.name }}</p>
          <p class="text-xs" style="color:var(--text-secondary)">{{ formatSize(selectedFile.size) }}</p>
        </div>
        <button @click="selectedFile = null; step = 1" class="text-gray-400 hover:text-red-500 transition-colors">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none"><line x1="18" y1="6" x2="6" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><line x1="6" y1="6" x2="18" y2="18" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
        </button>
      </div>

      <!-- Step 1: Survey type selection -->
      <div v-if="selectedFile && step === 1" class="mt-5 space-y-4">
        <div>
          <label class="block text-xs font-black uppercase tracking-widest text-gray-400 mb-2">Nom du projet</label>
          <input v-model="form.project_name" type="text" placeholder="ex : VOC EBU Janvier 2026" class="input-base" />
        </div>

        <div>
          <label class="block text-xs font-black uppercase tracking-widest text-gray-400 mb-2">Type d'enquête</label>
          <div class="grid grid-cols-2 gap-2 sm:grid-cols-4">
            <button v-for="t in surveyTypes" :key="t"
              @click="form.survey_type = t"
              class="py-2.5 px-3 rounded-xl border-2 text-sm font-bold transition-all"
              :class="form.survey_type === t ? 'border-yellow-400 bg-yellow-50 text-yellow-800' : 'border-gray-200 text-gray-500 hover:border-gray-300'">
              {{ t }}
            </button>
          </div>
          <input v-if="!surveyTypes.includes(form.survey_type)" v-model="form.survey_type"
            placeholder="Autre type..." class="input-base mt-2" />
        </div>

        <!-- New vs existing template -->
        <div v-if="form.survey_type">
          <label class="block text-xs font-black uppercase tracking-widest text-gray-400 mb-2">Configuration</label>
          <div class="grid grid-cols-2 gap-3">
            <button @click="form.is_new = true"
              class="p-4 rounded-xl border-2 text-left transition-all"
              :class="form.is_new ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 hover:border-gray-300'">
              <div class="flex items-center gap-2 mb-1">
                <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
                     :style="form.is_new ? 'background:#FFCC00' : 'background:#E5E7EB'">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none"><path d="M12 5v14m-7-7h14" stroke="currentColor" stroke-width="3" stroke-linecap="round"/></svg>
                </div>
                <span class="font-bold text-sm text-gray-800">Première fois</span>
              </div>
              <p class="text-xs text-gray-500">Je vais nommer mes colonnes une par une</p>
            </button>

            <button @click="selectExisting"
              class="p-4 rounded-xl border-2 text-left transition-all"
              :style="!form.is_new && form.is_new !== null ? 'border:2px solid #23221E;background:#FAF9F5' : 'border:2px solid var(--border)'">
              <div class="flex items-center gap-2 mb-1">
                <div class="w-6 h-6 rounded-full flex items-center justify-center flex-shrink-0"
                     :style="form.is_new === false ? 'background:#23221E' : 'background:#E5E3DB'">
                  <svg width="10" height="10" viewBox="0 0 24 24" fill="none"><path d="M19 21l-7-5-7 5V5a2 2 0 012-2h10a2 2 0 012 2z" stroke="white" stroke-width="2.5" stroke-linecap="round"/></svg>
                </div>
                <span class="font-bold text-sm text-gray-800">Appliquer un modèle</span>
              </div>
              <p class="text-xs text-gray-500">J'ai déjà traité ce type — refais le tri automatiquement</p>
            </button>
          </div>

          <!-- Template selector (when "existing") -->
          <div v-if="form.is_new === false" class="mt-3">
            <div v-if="savedTemplates.length">
              <select v-model="form.template_id" class="input-base">
                <option value="">— Choisir un modèle sauvegardé —</option>
                <option v-for="t in filteredTemplates" :key="t.id" :value="t.id">
                  {{ t.name }}
                </option>
              </select>
            </div>
            <div v-else class="text-xs text-gray-400 mt-1">
              Aucun modèle pour l'instant. Choisissez « Première fois », nommez vos colonnes une fois, et la prochaine fois ce sera automatique.
            </div>
          </div>
        </div>

        <!-- Versions : ce type a déjà des traitements -->
        <div v-if="form.survey_type && existingCount > 0" class="p-4 rounded-xl" style="background:#FAF9F5;border:1px solid var(--border)">
          <p class="text-sm font-bold mb-1" style="color:var(--text-primary)">
            Vous avez déjà traité {{ existingCount }} fichier(s) « {{ form.survey_type }} »
          </p>
          <p class="text-xs mb-3" style="color:var(--text-muted)">Que faire de celui-ci ?</p>
          <div class="flex flex-col gap-2">
            <label class="flex items-start gap-2.5 cursor-pointer p-2 rounded-lg" style="border:1px solid var(--border)"
              :style="form.version_mode === 'NEW' ? 'background:white;border-color:#23221E' : ''">
              <input type="radio" value="NEW" v-model="form.version_mode" class="mt-0.5" />
              <span class="text-sm" style="color:var(--text-primary)">
                <strong>L'ajouter à côté des autres</strong>
                <span class="block text-xs" style="color:var(--text-muted)">Recommandé. Vos anciens fichiers restent intacts.</span>
              </span>
            </label>
            <label class="flex items-start gap-2.5 cursor-pointer p-2 rounded-lg" style="border:1px solid var(--border)"
              :style="form.version_mode === 'REPLACE' ? 'background:white;border-color:#23221E' : ''">
              <input type="radio" value="REPLACE" v-model="form.version_mode" class="mt-0.5" />
              <span class="text-sm" style="color:var(--text-primary)">
                <strong>Remplacer les anciens</strong>
                <span class="block text-xs" style="color:var(--text-muted)">Supprime vos traitements « {{ form.survey_type }} » précédents.</span>
              </span>
            </label>
            <label class="flex items-start gap-2.5 cursor-pointer p-2 rounded-lg" style="border:1px solid var(--border)"
              :style="form.version_mode === 'CONCAT' ? 'background:white;border-color:#23221E' : ''">
              <input type="radio" value="CONCAT" v-model="form.version_mode" class="mt-0.5" />
              <span class="text-sm" style="color:var(--text-primary)">
                <strong>Tout regrouper en un seul tableau</strong>
                <span class="block text-xs" style="color:var(--text-muted)">Empile ce fichier avec les précédents (utile pour un bilan trimestriel).</span>
              </span>
            </label>
          </div>
        </div>

        <button v-if="form.survey_type && form.is_new !== null && (form.is_new || form.template_id)"
          @click="upload" :disabled="uploading"
          class="btn-primary w-full mt-2 flex items-center justify-center gap-2">
          <svg v-if="uploading" class="animate-spin" width="15" height="15" viewBox="0 0 24 24" fill="none">
            <circle cx="12" cy="12" r="10" stroke="rgba(0,0,0,.2)" stroke-width="3"/>
            <path d="M12 2a10 10 0 0110 10" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
          </svg>
          {{ uploading ? 'Analyse en cours…' : 'Analyser et importer' }}
        </button>
      </div>
    </div>

    <!-- Recent imports -->
    <div class="bg-white rounded-2xl border border-border overflow-hidden">
      <div class="px-5 py-4 border-b border-border flex items-center justify-between">
        <h2 class="font-black text-sm uppercase tracking-widest text-gray-400" style="font-family:Montserrat,sans-serif">Imports récents</h2>
      </div>
      <div v-if="!imports.length" class="py-12 text-center text-gray-400">
        <svg class="mx-auto mb-3" width="36" height="36" viewBox="0 0 24 24" fill="none"><path d="M22 12h-4l-3 9L9 3l-3 9H2" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
        <p class="text-sm">Aucun import</p>
      </div>
      <table v-else class="w-full text-sm">
        <thead class="bg-gray-50 text-xs text-gray-500 uppercase tracking-wide">
          <tr>
            <th class="px-5 py-3 text-left font-semibold">Fichier</th>
            <th class="px-4 py-3 text-left font-semibold">Projet</th>
            <th class="px-4 py-3 text-left font-semibold">Type</th>
            <th class="px-4 py-3 text-left font-semibold">Lignes</th>
            <th class="px-4 py-3 text-left font-semibold">Statut</th>
            <th class="px-4 py-3 text-left font-semibold">Date</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="f in imports" :key="f.id" class="hover:bg-gray-50 transition-colors">
            <td class="px-5 py-3">
              <div class="flex items-center gap-2">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z" stroke="#9C998F" stroke-width="1.5" stroke-linecap="round"/><polyline points="14 2 14 8 20 8" stroke="#9C998F" stroke-width="1.5" stroke-linecap="round"/></svg>
                <span class="font-medium text-gray-700 truncate max-w-[180px]" :title="f.original_filename">{{ f.original_filename }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-500 text-xs">{{ f.project_name || '—' }}</td>
            <td class="px-4 py-3">
              <span v-if="f.survey_type" class="px-2 py-0.5 rounded-md text-xs font-semibold" style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB">{{ f.survey_type }}</span>
            </td>
            <td class="px-4 py-3 text-gray-600 text-xs">{{ f.total_rows?.toLocaleString('fr-FR') }}</td>
            <td class="px-4 py-3"><StatusBadge :status="f.status" /></td>
            <td class="px-4 py-3 text-xs text-gray-400">{{ fmtDate(f.created_at) }}</td>
            <td class="px-4 py-3">
              <!-- Le manager supervise les métadonnées : pas d'accès aux données des agents -->
              <div v-if="canAct(f)" class="flex gap-1.5">
                <router-link :to="`/import/${f.id}/configure`"
                  class="px-2.5 py-1 rounded-lg text-xs font-semibold border border-gray-200 text-gray-600 hover:bg-gray-100 transition-colors">
                  Configurer
                </router-link>
                <router-link v-if="['CLEANED','JOINED'].includes(f.status)" :to="`/import/${f.id}/join`"
                  class="px-2.5 py-1 rounded-lg text-xs font-bold transition-colors"
                  style="background:#FEFCE8;color:#854D0E;border:1px solid #FDE047">
                  Enrichir
                </router-link>
              </div>
              <span v-else class="text-xs" style="color:#D5D2C8">{{ f.user_name || '—' }}</span>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import api from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'
import StatusBadge from '@/components/StatusBadge.vue'

const router = useRouter()
const toast = useToast()
const auth = useAuthStore()

// Agir sur un fichier : son propriétaire ou l'admin (le manager consulte les métadonnées)
function canAct(f) {
  return auth.user?.role === 'ADMIN' || f.user === auth.user?.id
}

const selectedFile = ref(null)
const dragging = ref(false)
const uploading = ref(false)
const step = ref(1)
const imports = ref([])
const savedTemplates = ref([])
const builtinTypes = ref([])

const surveyTypes = ref(['VOC EBU', 'FTTH', '4G', 'Roaming'])

const form = ref({ project_name: '', survey_type: '', is_new: null, template_id: '', version_mode: 'NEW' })

// Traitements déjà réalisés pour ce type (pour proposer remplacer/concaténer)
const existingCount = computed(() =>
  imports.value.filter(f => f.survey_type === form.value.survey_type && ['CLEANED', 'JOINED'].includes(f.status)).length
)

const filteredTemplates = computed(() => {
  const byType = savedTemplates.value.filter(t => t.survey_type === form.value.survey_type)
  return byType.length ? byType : savedTemplates.value
})

async function loadTypes() {
  try {
    const { data } = await api.get('/imports/files/survey_types/')
    builtinTypes.value = data?.builtin || []
    savedTemplates.value = data?.saved || []
    if (data?.types?.length) surveyTypes.value = data.types
  } catch (e) {
    toast.add({ severity: 'warn', summary: 'Modèles non chargés', detail: 'Impossible de récupérer les modèles — vérifiez le serveur.', life: 4000 })
  }
}

// Recharge les modèles au moment du clic : liste toujours à jour
async function selectExisting() {
  form.value.is_new = false
  if (!savedTemplates.value.length) await loadTypes()
}

function onFileSelect(e) { selectedFile.value = e.target.files[0] || null }
function onDrop(e) { selectedFile.value = e.dataTransfer.files[0] || null; dragging.value = false }
function formatSize(b) { return b < 1024 ** 2 ? `${(b / 1024).toFixed(1)} Ko` : `${(b / 1024 ** 2).toFixed(1)} Mo` }
function fmtDate(d) { return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short', year: 'numeric' }) }

async function upload() {
  uploading.value = true
  try {
    const fd = new FormData()
    fd.append('file', selectedFile.value)
    fd.append('project_name', form.value.project_name)
    fd.append('survey_type', form.value.survey_type)
    fd.append('version_mode', form.value.version_mode)
    if (!form.value.is_new && form.value.template_id) fd.append('template_id', form.value.template_id)

    const { data } = await api.post('/imports/files/upload/', fd)
    if (data.status === 'ERROR') {
      toast.add({ severity: 'error', summary: 'Erreur d\'analyse', detail: data.error_message?.split('\n')[0] || 'Fichier non traitable', life: 8000 })
      return
    }
    if (data.auto_cleaned) {
      toast.add({ severity: 'success', summary: 'Nettoyage automatique réussi', detail: `${data.total_rows} lignes nettoyées avec le modèle`, life: 4000 })
      router.push(`/import/${data.id}/configure`)
    } else {
      toast.add({ severity: 'success', summary: 'Fichier analysé', detail: `${data.total_rows} lignes · ${data.total_columns} colonnes — nommez vos colonnes`, life: 4000 })
      router.push(`/import/${data.id}/configure`)
    }
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Erreur d\'import', detail: e.response?.data?.error || 'Fichier non traitable', life: 6000 })
  } finally {
    uploading.value = false
  }
}

onMounted(async () => {
  loadTypes()
  const imp = await api.get('/imports/files/').catch(() => ({ data: [] }))
  imports.value = imp.data?.results || imp.data || []
})
</script>
