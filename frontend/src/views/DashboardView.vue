<template>
  <div>
    <!-- Hero (mobile) -->
    <div class="lg:hidden rounded-2xl p-5 mb-5 relative overflow-hidden"
         style="background:linear-gradient(120deg,#1C1B18 0%,#4a3c12 52%,#9c7a10 100%)">
      <div class="absolute inset-0" aria-hidden="true"
           style="background-image:url('/mtn-pattern.png');background-size:170%;opacity:.07;filter:invert(1)"></div>
      <div class="relative flex items-center justify-between gap-3">
        <div class="min-w-0">
          <p class="text-xl font-black leading-tight text-white" style="font-family:Montserrat,sans-serif;letter-spacing:-.02em">
            Bonjour,<br/><span style="color:#FFCC00">{{ greetingName }}</span>
          </p>
          <p class="text-xs mt-2 leading-snug" style="color:rgba(255,255,255,.82)">Transformez vos enquêtes clients en décisions.</p>
        </div>
        <svg width="112" height="100" viewBox="0 0 112 100" class="flex-shrink-0">
          <rect x="34" y="14" width="58" height="68" rx="8" fill="rgba(255,255,255,.18)" transform="rotate(9 60 48)"/>
          <g transform="rotate(-6 54 52)">
            <rect x="22" y="20" width="60" height="70" rx="8" fill="#fff"/>
            <rect x="30" y="30" width="30" height="5" rx="2.5" fill="#E5E3DB"/>
            <rect x="30" y="40" width="20" height="5" rx="2.5" fill="#EFEDE6"/>
            <rect x="30" y="70" width="8" height="12" rx="2" fill="#FFCC00"/>
            <rect x="42" y="62" width="8" height="20" rx="2" fill="#FFD633"/>
            <rect x="54" y="54" width="8" height="28" rx="2" fill="#FFCC00"/>
            <rect x="66" y="66" width="8" height="16" rx="2" fill="#FFE066"/>
          </g>
          <circle cx="90" cy="76" r="16" fill="#FFCC00"/>
          <polyline points="82 80 87 74 91 77 97 70" fill="none" stroke="#1C1B18" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>
          <polyline points="93 70 97 70 97 74" fill="none" stroke="#1C1B18" stroke-width="2.3" stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
      </div>
    </div>

    <!-- En-tête (desktop) -->
    <div class="hidden lg:flex items-end justify-between gap-2 mb-5">
      <div>
        <h1 class="text-2xl font-black" style="color:#21201C;font-family:Montserrat,sans-serif;letter-spacing:-.02em">Tableau de bord</h1>
        <p class="text-sm mt-0.5" style="color:#9C998F">Vue d'ensemble de vos enquêtes et indicateurs clients</p>
      </div>
      <div class="flex items-center gap-2 px-3 py-2 rounded-lg bg-white self-start" style="border:1px solid var(--border)">
        <i class="pi pi-calendar text-sm" style="color:#9C998F"></i>
        <span class="text-sm font-medium" style="color:#6E6B63">{{ periodLabel }}</span>
      </div>
    </div>

    <div v-if="loading" class="bg-white rounded-2xl p-16 flex justify-center" style="border:1px solid var(--border)">
      <Spinner label="Chargement du tableau de bord…" />
    </div>

    <template v-else>
      <!-- Filtre par enquête -->
      <div class="flex flex-col sm:flex-row sm:items-center gap-2 mb-4">
        <div class="flex items-center gap-2">
          <span class="text-xs font-semibold whitespace-nowrap" style="color:#6E6B63">Afficher :</span>
          <select v-model="selectedType" @change="loadCore"
            class="flex-1 sm:flex-none px-3 py-2 rounded-lg text-sm bg-white" style="border:1px solid var(--border)">
            <option value="">Toutes les enquêtes</option>
            <option v-for="t in availableTypes" :key="t" :value="t">{{ t }}</option>
          </select>
          <i v-if="reloading" class="pi pi-spin pi-spinner text-xs" style="color:#9C998F"></i>
        </div>
        <span class="text-xs" style="color:#9C998F">{{ scopeLabel }}</span>
      </div>

      <!-- Cartes métriques -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-5">
        <MetricCard label="Enquêtes traitées" :value="formatNum(stats.total_reports)" icon="pi-inbox"
          tone="yellow" :trend="stats.files_trend" :spark="activitySpark" type="bar" />
        <MetricCard label="Score NPS" :value="stats.nps_global != null ? (stats.nps_global>0?'+':'')+stats.nps_global : '—'" icon="pi-star"
          tone="green" :trend="npsTrend" suffix=" pts" :spark="npsSpark" type="line" />
        <MetricCard label="Satisfaction client" :value="stats.satisfaction_pct != null ? stats.satisfaction_pct+'%' : '—'" icon="pi-face-smile"
          tone="yellow" :spark="npsSpark" type="line" />
        <MetricCard label="Taux d'insatisfaction" :value="stats.detraction_pct != null ? stats.detraction_pct+'%' : '—'" icon="pi-exclamation-triangle"
          tone="red" :spark="npsSpark" type="line" />
      </div>

      <!-- Ligne : courbe NPS + fichiers récents -->
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 mb-5">
        <!-- Évolution du NPS -->
        <div class="lg:col-span-2 bg-white rounded-2xl p-5" style="border:1px solid var(--border)">
          <div class="mb-4">
            <h2 class="font-bold text-sm" style="color:#21201C;font-family:Montserrat,sans-serif">Évolution du NPS</h2>
            <p class="text-xs mt-0.5" style="color:#9C998F">Score NPS moyen, mois par mois — pour suivre la tendance de satisfaction</p>
          </div>
          <div v-if="npsLine.length > 1">
            <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" style="height:auto">
              <defs>
                <linearGradient id="npsFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#FFCC00" stop-opacity="0.28"/>
                  <stop offset="100%" stop-color="#FFCC00" stop-opacity="0"/>
                </linearGradient>
              </defs>
              <!-- Graduations Y (échelle NPS) -->
              <g v-for="tk in gridTicks" :key="tk">
                <line :x1="PADL" :x2="W-PADR" :y1="yAt(tk)" :y2="yAt(tk)" stroke="#F0EEE7" stroke-width="1"/>
                <text :x="PADL-8" :y="yAt(tk)+4" text-anchor="end" style="font-size:11px;fill:#B8B5AC">{{ tk>0?'+':'' }}{{ tk }}</text>
              </g>
              <path :d="areaPath" fill="url(#npsFill)"/>
              <path :d="linePath" fill="none" stroke="#E9A800" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
              <!-- Points + valeur -->
              <g v-for="(p,i) in npsPts" :key="i">
                <circle :cx="p.x" :cy="p.y" r="4" fill="#FFCC00" stroke="#fff" stroke-width="2"/>
                <text :x="p.x" :y="p.y-11" text-anchor="middle" style="font-size:12px;font-weight:700;fill:#21201C;font-family:Montserrat">{{ p.nps>0?'+':'' }}{{ p.nps }}</text>
                <text :x="p.x" :y="H-6" text-anchor="middle" style="font-size:11px;fill:#9C998F">{{ npsLine[i].label }}</text>
              </g>
            </svg>
          </div>
          <div v-else class="py-14 text-center text-sm" style="color:#9C998F">
            <i class="pi pi-chart-line text-2xl block mb-2"></i>
            Pas encore assez de données. Traitez au moins deux fichiers pour voir la tendance.
          </div>
        </div>

        <!-- Derniers fichiers traités -->
        <div class="bg-white rounded-2xl p-5" style="border:1px solid var(--border)">
          <h2 class="font-bold text-sm mb-4" style="color:#21201C;font-family:Montserrat,sans-serif">Derniers fichiers traités</h2>
          <div v-if="!stats.recent_files?.length" class="py-8 text-center text-sm" style="color:#9C998F">Aucun fichier</div>
          <div v-else class="space-y-1">
            <router-link v-for="f in stats.recent_files" :key="f.id" :to="`/import/${f.id}/configure`"
              class="flex items-center gap-3 p-2 rounded-lg hover:bg-[#FAF9F5] transition-colors">
              <div class="w-8 h-9 rounded flex items-center justify-center flex-shrink-0" :style="`background:${fileIcon(f.name).bg}`">
                <i :class="`pi ${fileIcon(f.name).icon} text-sm`" :style="`color:${fileIcon(f.name).color}`"></i>
              </div>
              <div class="flex-1 min-w-0">
                <p class="text-xs font-semibold truncate" style="color:#21201C">{{ f.name }}</p>
                <p class="text-xs" style="color:#9C998F">{{ formatDate(f.date) }}</p>
              </div>
              <StatusBadge :status="f.status" />
            </router-link>
          </div>
        </div>
      </div>

      <!-- Ligne : sentiments + NPS par type -->
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-4">
        <!-- Répartition des sentiments -->
        <div class="bg-white rounded-2xl p-5" style="border:1px solid var(--border)">
          <h2 class="font-bold text-sm" style="color:#21201C;font-family:Montserrat,sans-serif">Répartition des sentiments</h2>
          <p class="text-xs mb-4 mt-0.5" style="color:#9C998F">Sur l'ensemble des réponses du périmètre affiché</p>
          <div v-if="sent.total > 0" class="flex items-center gap-6">
            <svg width="150" height="150" viewBox="0 0 140 140" class="flex-shrink-0">
              <circle cx="70" cy="70" :r="R" fill="none" stroke="#F0EEE7" stroke-width="18"/>
              <circle cx="70" cy="70" :r="R" fill="none" stroke="#21A05A" stroke-width="18"
                :stroke-dasharray="`${arc(sent.promoters)} ${C}`" stroke-dashoffset="0" transform="rotate(-90 70 70)" stroke-linecap="butt"/>
              <circle cx="70" cy="70" :r="R" fill="none" stroke="#FFCC00" stroke-width="18"
                :stroke-dasharray="`${arc(sent.passives)} ${C}`" :stroke-dashoffset="-arc(sent.promoters)" transform="rotate(-90 70 70)"/>
              <circle cx="70" cy="70" :r="R" fill="none" stroke="#D4452C" stroke-width="18"
                :stroke-dasharray="`${arc(sent.detractors)} ${C}`" :stroke-dashoffset="-arc(sent.promoters+sent.passives)" transform="rotate(-90 70 70)"/>
              <text x="70" y="66" text-anchor="middle" style="font-size:20px;font-weight:800;fill:#21201C;font-family:Montserrat">{{ formatNum(sent.total) }}</text>
              <text x="70" y="84" text-anchor="middle" style="font-size:10px;fill:#9C998F">réponses</text>
            </svg>
            <div class="space-y-2.5 flex-1">
              <div v-for="s in sentLegend" :key="s.label" class="flex items-center justify-between">
                <span class="flex items-center gap-2 text-sm" style="color:#6E6B63">
                  <span class="w-2.5 h-2.5 rounded-full" :style="`background:${s.color}`"></span>{{ s.label }}
                </span>
                <span class="text-sm font-bold" style="color:#21201C">{{ s.pct }}%</span>
              </div>
            </div>
          </div>
          <div v-else class="py-12 text-center text-sm" style="color:#9C998F">Pas encore de données NPS</div>
        </div>

        <!-- NPS par enquête -->
        <div class="bg-white rounded-2xl p-5" style="border:1px solid var(--border)">
          <h2 class="font-bold text-sm mb-1" style="color:#21201C;font-family:Montserrat,sans-serif">NPS par enquête</h2>
          <p class="text-xs mb-4" style="color:#9C998F">Score le plus récent · variation vs période précédente</p>
          <div v-if="npsSummary.length" class="space-y-3">
            <div v-for="s in npsSummary" :key="s.survey_type">
              <div class="flex items-center justify-between text-xs mb-1">
                <span style="color:#6E6B63">{{ s.survey_type }}</span>
                <span class="font-bold flex items-center gap-1.5">
                  <span :style="`color:${npsColor(s.latest_nps)}`">{{ s.latest_nps>0?'+':'' }}{{ s.latest_nps }}</span>
                  <span v-if="s.delta != null" :style="`color:${s.delta>=0?'#21A05A':'#D4452C'}`">({{ s.delta>=0?'+':'' }}{{ s.delta }})</span>
                </span>
              </div>
              <div class="h-2 rounded-full" style="background:#F0EEE7">
                <div class="h-2 rounded-full" :style="`width:${(s.latest_nps+100)/2}%;background:${npsColor(s.latest_nps)}`"></div>
              </div>
            </div>
          </div>
          <div v-else class="py-12 text-center text-sm" style="color:#9C998F">Aucune donnée</div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/composables/useApi'
import MetricCard from '@/components/MetricCard.vue'
import StatusBadge from '@/components/StatusBadge.vue'
import Spinner from '@/components/Spinner.vue'

const auth = useAuthStore()
const loading = ref(true)
const reloading = ref(false)
const stats = ref({})
const npsSummary = ref([])
const npsSeries = ref({})
const dailyCounts = ref([])
const selectedType = ref('')
const availableTypes = computed(() => stats.value.available_types || [])

const scopeLabel = computed(() => {
  const who = stats.value.is_supervisor ? ' · toute l\'équipe' : ''
  return selectedType.value
    ? `Chiffres de l'enquête « ${selectedType.value} »${who}`
    : `Toutes vos enquêtes confondues${who}`
})

const periodLabel = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
})

const ROLES = { ADMIN: 'Administrateur', MANAGER: 'Manager CX', AGENT: 'Agent CX' }
const greetingName = computed(() => auth.user?.first_name || ROLES[auth.user?.role] || 'bienvenue')

// Icône selon le type de fichier (Excel vert, PDF rouge, Word bleu…)
function fileIcon(name) {
  const ext = (name || '').split('.').pop().toLowerCase()
  if (['xlsx', 'xls', 'csv'].includes(ext)) return { icon: 'pi-file-excel', bg: '#E6F4EA', color: '#1A8049' }
  if (ext === 'pdf') return { icon: 'pi-file-pdf', bg: '#FDECEC', color: '#C13C27' }
  if (['doc', 'docx'].includes(ext)) return { icon: 'pi-file-word', bg: '#E7EEFB', color: '#2B579A' }
  return { icon: 'pi-file', bg: '#F0EEE7', color: '#6E6B63' }
}

const sent = computed(() => stats.value.sentiment || { promoters:0, passives:0, detractors:0, total:0 })
const sentLegend = computed(() => {
  const s = sent.value, tot = s.total || 1
  return [
    { label:'Promoteurs (9-10)', color:'#21A05A', pct: Math.round(s.promoters/tot*100) },
    { label:'Passifs (7-8)', color:'#FFCC00', pct: Math.round(s.passives/tot*100) },
    { label:'Détracteurs (0-6)', color:'#D4452C', pct: Math.round(s.detractors/tot*100) },
  ]
})
const R = 54, C = 2 * Math.PI * 54
function arc(v) { return sent.value.total ? (v / sent.value.total) * C : 0 }

// Sparkline enquêtes = activité 14 jours
const activitySpark = computed(() => dailyCounts.value.length ? dailyCounts.value : [])
// Courbe NPS = NPS MOYEN PAR MOIS (filtrée si une enquête est choisie)
const npsLine = computed(() => {
  const src = selectedType.value
    ? { [selectedType.value]: npsSeries.value[selectedType.value] || [] }
    : npsSeries.value
  const byMonth = {}
  Object.values(src).forEach(arr => (arr || []).forEach(p => {
    const d = new Date(p.date)
    const key = `${d.getFullYear()}-${String(d.getMonth()).padStart(2, '0')}`
    if (!byMonth[key]) byMonth[key] = { sum: 0, count: 0, date: new Date(d.getFullYear(), d.getMonth(), 1) }
    byMonth[key].sum += p.nps
    byMonth[key].count++
  })
  )
  const months = Object.values(byMonth).sort((a, b) => a.date - b.date)
  const multiYear = new Set(months.map(m => m.date.getFullYear())).size > 1
  return months.map(m => ({
    nps: Math.round(m.sum / m.count * 10) / 10,
    label: m.date.toLocaleDateString('fr-FR', multiYear ? { month: 'short', year: '2-digit' } : { month: 'short' }),
  }))
})
const npsSpark = computed(() => npsLine.value.map(p => p.nps + 100))
const npsTrend = computed(() => npsLine.value.length > 1 ? Math.round(npsLine.value[npsLine.value.length-1].nps - npsLine.value[0].nps) : null)

// Courbe NPS : échelle réelle graduée (0..100 si tout positif, sinon -100..100)
const W = 720, H = 240, PADL = 38, PADR = 16, PADT = 26, PADB = 28
const chartMin = computed(() => npsLine.value.some(p => p.nps < 0) ? -100 : 0)
const chartMax = 100
function yAt(val) { return PADT + (1 - (val - chartMin.value) / (chartMax - chartMin.value)) * (H - PADT - PADB) }
const gridTicks = computed(() => {
  const min = chartMin.value, n = 4
  return Array.from({ length: n + 1 }, (_, i) => Math.round(min + (chartMax - min) * i / n))
})
const npsPts = computed(() => {
  const n = npsLine.value.length
  return npsLine.value.map((p, i) => ({
    x: PADL + (n === 1 ? 0.5 : i / (n - 1)) * (W - PADL - PADR),
    y: yAt(p.nps),
    nps: p.nps,
  }))
})
const linePath = computed(() => {
  const pts = npsPts.value
  if (pts.length < 2) return ''
  let d = `M${pts[0].x},${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    const a = pts[i-1], b = pts[i], mx = (a.x+b.x)/2
    d += ` C${mx},${a.y} ${mx},${b.y} ${b.x},${b.y}`
  }
  return d
})
const areaPath = computed(() => npsPts.value.length < 2 ? '' : `${linePath.value} L${W-PADR},${yAt(chartMin.value)} L${PADL},${yAt(chartMin.value)} Z`)

function npsColor(n) { return n >= 50 ? '#21A05A' : n >= 0 ? '#B7791F' : '#D4452C' }
function formatNum(n) { return (n || 0).toLocaleString('fr-FR') }
function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR', { day:'2-digit', month:'short', year:'numeric' }) }

async function loadCore() {
  reloading.value = true
  try {
    const { data } = await api.get('/dashboard/agent/', { params: selectedType.value ? { survey_type: selectedType.value } : {} })
    stats.value = data
  } finally { reloading.value = false }
}

onMounted(async () => {
  try {
    const [core, ev, files] = await Promise.all([
      api.get('/dashboard/agent/'),
      api.get('/history/reports/nps_evolution/').catch(() => ({ data: {} })),
      api.get('/imports/files/').catch(() => ({ data: [] })),
    ])
    stats.value = core.data
    npsSummary.value = ev.data?.summary || []
    npsSeries.value = ev.data?.series || {}
    // Activité 14 jours
    const list = files.data?.results || files.data || []
    const counts = Array(14).fill(0)
    const today = new Date(); today.setHours(0,0,0,0)
    list.forEach(f => {
      const d = new Date(f.created_at); d.setHours(0,0,0,0)
      const diff = Math.round((today - d) / 86400000)
      if (diff >= 0 && diff < 14) counts[13 - diff]++
    })
    dailyCounts.value = counts
  } finally {
    loading.value = false
  }
})
</script>
