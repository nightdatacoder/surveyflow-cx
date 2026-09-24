<template>
  <div class="space-y-6">
    <!-- Step indicator -->
    <div class="bg-white rounded-xl shadow-sm p-5">
      <div class="flex items-center gap-4">
        <StepBadge :n="1" :done="step > 1" :active="step === 1" icon="pi-file" label="Fichier de référence" />
        <div class="flex-1 h-px" style="background:var(--border)"></div>
        <StepBadge :n="2" :done="step > 2" :active="step === 2" icon="pi-link" label="Liaison" />
        <div class="flex-1 h-px" style="background:var(--border)"></div>
        <StepBadge :n="3" :done="step === 3" :active="step === 3" icon="pi-table" label="Résultat" />
      </div>
    </div>

    <!-- Step 1: Upload ref file -->
    <div v-if="step === 1" class="bg-white rounded-xl shadow-sm p-6">
      <h2 class="font-bold mb-1" style="color:var(--text-primary);font-family:Montserrat,sans-serif">Ajouter les infos clients</h2>
      <p class="text-sm mb-4" style="color:var(--text-secondary)">
        Déposez le fichier qui contient les infos clients (ex : liste de tickets).
        Le logiciel trouvera tout seul la colonne N° REC pour relier les deux fichiers.
      </p>

      <div @click="$refs.refInput.click()" @dragover.prevent @drop.prevent="e => refFile = e.dataTransfer.files[0]"
        class="border border-dashed rounded-xl p-8 text-center cursor-pointer transition-all"
        :style="refFile ? 'border-color:#23221E;background:#FAF9F5' : 'border-color:#D5D2C8'">
        <input ref="refInput" type="file" accept=".xlsx,.xls,.csv" class="hidden" @change="e => refFile = e.target.files[0]" />
        <i class="pi pi-file-import text-2xl mb-2 block" :style="refFile ? 'color:#21201C' : 'color:#9C998F'"></i>
        <p class="text-sm font-medium" :style="refFile ? 'color:#21201C' : 'color:#6E6B63'">
          {{ refFile ? refFile.name : 'Cliquez ou glissez le fichier de référence' }}
        </p>
      </div>

      <button v-if="refFile && !analyzing" @click="analyzeRef" class="btn-primary mt-4">
        Analyser le fichier
      </button>

      <!-- Barre de progression -->
      <div v-if="analyzing" class="mt-4">
        <div class="flex items-center justify-between mb-1.5">
          <span class="text-xs font-semibold" style="color:var(--text-primary)">{{ progressStage }}</span>
          <span class="text-xs font-bold" style="color:var(--text-secondary)">{{ Math.round(progress) }}%</span>
        </div>
        <div class="w-full rounded-full h-2 overflow-hidden" style="background:#EFEDE6">
          <div class="h-2 rounded-full" style="background:#FFCC00;transition:width 0.4s ease"
            :style="`width:${progress}%`"></div>
        </div>
        <p class="text-xs mt-2" style="color:var(--text-muted)">
          Pour un gros classeur (50 000+ lignes), comptez environ une minute. La jointure sera ensuite immédiate.
        </p>
      </div>
    </div>

    <!-- Step 2: Configure join -->
    <div v-if="step === 2" class="space-y-4">
      <div class="bg-white rounded-xl shadow-sm p-6">
        <h2 class="font-semibold text-gray-700 mb-1">Choisissez les infos à ajouter</h2>
        <p class="text-xs text-gray-400 mb-4">La liaison est déjà réglée automatiquement — cochez simplement les colonnes qui vous intéressent puis lancez.</p>

        <!-- Sheet selection -->
        <div class="mb-4" v-if="Object.keys(refInfo.ref_sheets?.sheets || {}).length > 1">
          <label class="block text-sm font-medium text-gray-600 mb-1">Feuille du fichier de référence</label>
          <select v-model="joinConfig.ref_sheet"
            class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-yellow-400">
            <option v-for="(cols, sheet) in refInfo.ref_sheets.sheets" :key="sheet" :value="sheet">
              {{ sheet }} ({{ cols.length }} colonnes)
            </option>
          </select>
        </div>

        <!-- Liaison auto-détectée -->
        <div v-if="joinConfig.left_key && joinConfig.right_key && !showAdvanced"
          class="mb-4 p-4 rounded-xl flex items-center gap-3" style="background:#FAF9F5;border:1px solid var(--border)">
          <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#23221E">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M10 13a5 5 0 007.54.54l3-3a5 5 0 00-7.07-7.07l-1.72 1.71" stroke="#FFCC00" stroke-width="2" stroke-linecap="round"/><path d="M14 11a5 5 0 00-7.54-.54l-3 3a5 5 0 007.07 7.07l1.71-1.71" stroke="#FFCC00" stroke-width="2" stroke-linecap="round"/></svg>
          </div>
          <div class="flex-1">
            <p class="text-sm font-bold" style="color:var(--text-primary)">Les deux fichiers seront reliés par le numéro de ticket</p>
            <p class="text-xs mt-0.5" style="color:var(--text-secondary)">{{ joinConfig.left_key }} ↔ {{ joinConfig.right_key }} · feuille « {{ joinConfig.ref_sheet }} »</p>
          </div>
          <button @click="showAdvanced = true" class="text-xs underline" style="color:var(--text-secondary)">Modifier</button>
        </div>
        <div v-else class="mb-4 p-4 rounded-xl" style="background:#FAF9F5;border:1px solid var(--border)">
          <p class="text-sm font-bold" style="color:var(--text-primary)">Quelle colonne est commune aux deux fichiers ?</p>
          <p class="text-xs mt-0.5" style="color:var(--text-secondary)">C'est elle qui permet de relier vos réponses aux infos clients (ex : le N° REC, ou le numéro de téléphone).</p>
        </div>

        <!-- Choix des clés -->
        <div v-if="showAdvanced || !joinConfig.left_key" class="mb-5 p-4 rounded-xl space-y-4" style="background:#FAF9F5;border:1px solid var(--border)">
          <div class="grid grid-cols-2 gap-4">
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Colonne dans votre fichier</label>
              <select v-model="joinConfig.left_key"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-yellow-400 bg-white">
                <option value="">— Sélectionner —</option>
                <option v-for="c in refInfo.main_columns" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
            <div>
              <label class="block text-xs font-semibold text-gray-500 mb-1">Colonne dans le fichier déposé</label>
              <select v-model="joinConfig.right_key"
                class="w-full px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-yellow-400 bg-white">
                <option value="">— Sélectionner —</option>
                <option v-for="c in currentSheetCols" :key="c" :value="c">{{ c }}</option>
              </select>
            </div>
          </div>
          <div>
            <label class="block text-xs font-semibold text-gray-500 mb-1.5">Que garder dans le résultat ?</label>
            <div class="flex flex-col gap-1.5">
              <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="radio" value="LEFT" v-model="joinConfig.join_type" />
                Toutes mes réponses, même celles sans info client <span class="text-xs text-gray-400">(recommandé)</span>
              </label>
              <label class="flex items-center gap-2 text-sm text-gray-600 cursor-pointer">
                <input type="radio" value="INNER" v-model="joinConfig.join_type" />
                Seulement les réponses dont on a trouvé les infos client
              </label>
            </div>
          </div>
        </div>

        <!-- Columns to add -->
        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-600 mb-2">Infos clients à ajouter à votre fichier</label>
          <div class="flex flex-wrap gap-2 max-h-40 overflow-y-auto p-3 border border-gray-200 rounded-lg">
            <label v-for="c in currentSheetCols.filter(c => c !== joinConfig.right_key)" :key="c"
              class="flex items-center gap-2 px-3 py-1.5 rounded-lg cursor-pointer transition-all text-sm"
              :style="joinConfig.columns_to_add.includes(c)
                ? 'border:1.5px solid #23221E;background:#23221E;color:#F5F4EF'
                : 'border:1px solid var(--border);color:var(--text-secondary)'">
              <input type="checkbox" :value="c" v-model="joinConfig.columns_to_add" class="hidden" />
              <svg v-if="joinConfig.columns_to_add.includes(c)" width="11" height="11" viewBox="0 0 24 24" fill="none"><polyline points="20 6 9 17 4 12" stroke="#FFCC00" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/></svg>
              <svg v-else width="11" height="11" viewBox="0 0 24 24" fill="none"><rect x="4" y="4" width="16" height="16" rx="3" stroke="currentColor" stroke-width="2"/></svg>
              {{ c }}
            </label>
          </div>
          <div class="flex gap-2 mt-2">
            <button @click="selectAllCols" class="text-xs hover:underline" style="color:var(--text-secondary)">Tout sélectionner</button>
            <span style="color:#D5D2C8">|</span>
            <button @click="joinConfig.columns_to_add = []" class="text-xs hover:underline" style="color:var(--text-muted)">Tout désélectionner</button>
          </div>
        </div>

        <div class="flex gap-3 mt-5">
          <button @click="step = 1" class="btn-secondary">
            <i class="pi pi-arrow-left mr-1"></i>Retour
          </button>
          <button @click="executeJoin" :disabled="joining || !joinConfig.left_key || !joinConfig.right_key"
            class="btn-primary"
            :class="(joining || !joinConfig.left_key || !joinConfig.right_key) ? 'opacity-60 cursor-not-allowed' : ''">
            <i v-if="joining" class="pi pi-spin pi-spinner mr-2"></i>
            {{ joining ? 'Un instant…' : 'Lancer' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Step 3: Result -->
    <div v-if="step === 3 && joinResult" class="space-y-4">
      <div class="bg-white rounded-xl shadow-sm p-6">
        <div class="flex items-center gap-4 mb-5">
          <div class="w-11 h-11 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#23221E">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none"><polyline points="20 6 9 17 4 12" stroke="#FFCC00" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"/></svg>
          </div>
          <div>
            <h2 class="font-bold" style="color:var(--text-primary);font-family:Montserrat,sans-serif">Infos clients ajoutées</h2>
            <p class="text-sm mt-0.5" style="color:var(--text-secondary)">
              {{ joinResult.rows.toLocaleString() }} lignes · {{ joinResult.columns.length }} colonnes ·
              <span class="font-semibold" style="color:var(--text-primary)">{{ joinResult.match_rate }}% de correspondance</span>
            </p>
          </div>
        </div>

        <!-- Match rate bar -->
        <div class="mb-5">
          <div class="flex justify-between text-xs mb-1" style="color:var(--text-secondary)">
            <span>Taux de correspondance ({{ joinConfig.left_key }} ↔ {{ joinConfig.right_key }})</span>
            <span class="font-semibold" style="color:var(--text-primary)">{{ joinResult.match_rate }}%</span>
          </div>
          <div class="h-2 rounded-full" style="background:#EFEDE6">
            <div class="h-2 rounded-full transition-all"
                 :style="`width:${joinResult.match_rate}%;background:#FFCC00`"></div>
          </div>
          <p v-if="joinResult.match_rate < 80" class="text-xs mt-1.5" style="color:var(--text-muted)">
            Certaines lignes n'ont pas trouvé de correspondance — vérifiez que le fichier de tickets couvre la même période.
          </p>
        </div>

        <!-- Correction automatique des clés (téléphone, n° abonné... à la place du REC) -->
        <div v-if="joinResult.rescued > 0" class="mb-4 p-3 rounded-xl flex items-start gap-2.5"
          style="background:#FAF9F5;border:1px solid var(--border)">
          <svg class="flex-shrink-0 mt-0.5" width="14" height="14" viewBox="0 0 24 24" fill="none"><path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" stroke="#B7791F" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/></svg>
          <div class="text-xs" style="color:var(--text-secondary)">
            <span class="font-bold" style="color:var(--text-primary)">{{ joinResult.rescued }} ligne(s) corrigée(s) et uniformisée(s)</span>
            — l'agent avait saisi une autre valeur que le N° REC ; elle a été remplacée par le bon N° REC dans le fichier final. Retrouvée via :
            <span v-for="(n, col) in joinResult.rescued_by" :key="col" class="inline-block px-1.5 py-0.5 rounded ml-1"
              style="background:white;border:1px solid var(--border);color:var(--text-primary)">{{ col }} ({{ n }})</span>
          </div>
        </div>
        <div v-if="joinResult.unmatched > 0" class="mb-4 p-3 rounded-xl text-xs"
          style="background:#FAF9F5;border:1px solid var(--border);color:var(--text-secondary)">
          <span class="font-bold" style="color:var(--text-primary)">{{ joinResult.unmatched }} ligne(s) sans correspondance.</span>
          Valeurs introuvables dans le fichier de référence :
          <code v-for="v in joinResult.unmatched_sample" :key="v" class="px-1.5 py-0.5 rounded ml-1"
            style="background:white;border:1px solid var(--border)">{{ v }}</code>
        </div>

        <!-- Preview table -->
        <div class="overflow-x-auto">
          <table class="text-xs w-full">
            <thead>
              <tr class="bg-gray-50">
                <th v-for="col in joinResult.columns.slice(0,12)" :key="col" class="px-2 py-2 text-left font-semibold text-gray-600 whitespace-nowrap">
                  {{ col }}
                </th>
                <th v-if="joinResult.columns.length > 12" class="px-2 py-2 text-gray-400">+{{ joinResult.columns.length - 12 }} cols…</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-100">
              <tr v-for="(row, i) in joinResult.preview" :key="i" class="hover:bg-gray-50">
                <td v-for="col in joinResult.columns.slice(0,12)" :key="col" class="px-2 py-1.5 text-gray-600 max-w-[150px] truncate">
                  {{ row[col] || '—' }}
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Export buttons -->
        <div class="flex gap-3 mt-5 pt-5 border-t">
          <ExportButton :file-id="fileId" mode="joined" format="xlsx" label="Exporter XLSX enrichi" primary />
          <ExportButton :file-id="fileId" mode="joined" format="csv" label="Exporter CSV" />
          <ExportButton :file-id="fileId" mode="cleaned" format="xlsx" label="Exporter nettoyé seulement" />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRoute } from 'vue-router'
import { useToast } from 'primevue/usetoast'
import api from '@/composables/useApi'
import StepBadge from '@/components/StepBadge.vue'
import ExportButton from '@/components/ExportButton.vue'

const route = useRoute()
const toast = useToast()
const fileId = route.params.id

const step = ref(1)
const refFile = ref(null)
const analyzing = ref(false)
const joining = ref(false)
const refInfo = ref({ ref_sheets: { sheets: {} }, main_columns: [], key_suggestions: {} })
const joinResult = ref(null)

const joinConfig = ref({
  join_type: 'LEFT',
  ref_sheet: '',
  left_key: '',
  right_key: '',
  columns_to_add: [],
})

const showAdvanced = ref(false)
const progress = ref(0)
const progressStage = ref('')
let progressTimer = null

// Progression estimée d'après la taille du fichier (lecture xlsx = goulot d'étranglement)
function startProgress() {
  progress.value = 0
  const sizeMb = (refFile.value?.size || 0) / 1024 / 1024
  // ~12 s par Mo pour la lecture xlsx ; on vise 90% sur cette durée estimée
  const estimateMs = Math.max(4000, sizeMb * 12000)
  const stages = [
    [15, 'Ouverture du classeur…'],
    [45, 'Lecture des feuilles…'],
    [75, 'Recherche de la colonne N° REC…'],
    [90, 'Préparation de la liaison…'],
  ]
  const start = Date.now()
  progressTimer = setInterval(() => {
    const ratio = Math.min((Date.now() - start) / estimateMs, 1)
    progress.value = Math.min(ratio * 90, 90)
    progressStage.value = (stages.find(s => progress.value < s[0]) || stages[3])[1]
  }, 200)
}
function finishProgress() {
  clearInterval(progressTimer)
  progress.value = 100
  progressStage.value = 'Terminé'
}

const currentSheetCols = computed(() => {
  const sheet = joinConfig.value.ref_sheet
  return refInfo.value.ref_sheets?.sheets?.[sheet] || []
})

function selectAllCols() {
  joinConfig.value.columns_to_add = currentSheetCols.value.filter(c => c !== joinConfig.value.right_key)
}

async function analyzeRef() {
  analyzing.value = true
  startProgress()
  const fd = new FormData()
  fd.append('ref_file', refFile.value)
  fd.append('main_file_id', fileId)
  try {
    const { data } = await api.post('/joins/analyze_ref/', fd)
    finishProgress()
    refInfo.value = data
    const sheets = Object.keys(data.ref_sheets?.sheets || {})
    // Choisir automatiquement la feuille qui contient le N° REC
    joinConfig.value.ref_sheet = data.best_sheet || sheets[0] || ''
    const best = (data.key_suggestions?.[joinConfig.value.ref_sheet] || [])[0]
    if (best && best.is_rec_key) {
      // N° REC trouvé des deux côtés (cas VOC) : liaison réglée automatiquement
      joinConfig.value.left_key = best.left_col
      joinConfig.value.right_key = best.right_col
      toast.add({ severity: 'success', summary: 'Clé trouvée automatiquement',
        detail: `${best.left_col} ↔ ${best.right_col} (feuille « ${joinConfig.value.ref_sheet} »)`, life: 4000 })
    } else {
      // Pas de N° REC : on demande à l'utilisateur de choisir sa clé
      if (best) {
        joinConfig.value.left_key = best.left_col
        joinConfig.value.right_key = best.right_col
      }
      showAdvanced.value = true
    }
    step.value = 2
  } catch (e) {
    clearInterval(progressTimer)
    toast.add({ severity: 'error', summary: 'Erreur', detail: e.response?.data?.error || 'Analyse échouée', life: 5000 })
  } finally {
    analyzing.value = false
  }
}

async function executeJoin() {
  joining.value = true
  const fd = new FormData()
  fd.append('ref_file', refFile.value)
  fd.append('main_file_id', fileId)
  fd.append('left_key', joinConfig.value.left_key)
  fd.append('right_key', joinConfig.value.right_key)
  fd.append('join_type', joinConfig.value.join_type)
  fd.append('ref_sheet', joinConfig.value.ref_sheet)
  joinConfig.value.columns_to_add.forEach(c => fd.append('columns_to_add[]', c))
  try {
    const { data } = await api.post('/joins/execute/', fd)
    joinResult.value = data
    step.value = 3
    toast.add({ severity: 'success', summary: 'Jointure réussie', detail: `${data.match_rate}% de correspondance`, life: 3000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Erreur', detail: e.response?.data?.error || 'Jointure échouée', life: 5000 })
  } finally {
    joining.value = false
  }
}
</script>
