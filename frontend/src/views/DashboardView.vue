<template>
  <div>
    <!-- En-tête -->
    <div class="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-2 mb-5">
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
      <!-- Cartes métriques -->
      <div class="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4 mb-5">
        <MetricCard label="Total d'enquêtes" :value="formatNum(stats.total_reports)" icon="pi-users"
          tone="yellow" :trend="stats.files_trend" :spark="activitySpark" type="bar" />
        <MetricCard label="NPS global" :value="stats.nps_global != null ? (stats.nps_global>0?'+':'')+stats.nps_global : '—'" icon="pi-star"
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
          <h2 class="font-bold text-sm mb-4" style="color:#21201C;font-family:Montserrat,sans-serif">Évolution du NPS</h2>
          <div v-if="npsLine.length > 1">
            <svg :viewBox="`0 0 ${W} ${H}`" class="w-full" :style="`height:${H}px`" preserveAspectRatio="none">
              <defs>
                <linearGradient id="npsFill" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stop-color="#FFCC00" stop-opacity="0.28"/>
                  <stop offset="100%" stop-color="#FFCC00" stop-opacity="0"/>
                </linearGradient>
              </defs>
              <line v-for="(g,i) in 5" :key="i" :x1="PADL" :x2="W-PADR" :y1="yAt(i*25)" :y2="yAt(i*25)" stroke="#F0EEE7" stroke-width="1"/>
              <path :d="areaPath" fill="url(#npsFill)"/>
              <path :d="linePath" fill="none" stroke="#E9A800" stroke-width="2.5" stroke-linejoin="round" stroke-linecap="round"/>
              <circle v-for="(p,i) in npsPts" :key="i" :cx="p.x" :cy="p.y" r="3.5" fill="#FFCC00" stroke="#fff" stroke-width="2"/>
            </svg>
            <div class="flex justify-between mt-1 px-1">
              <span v-for="(p,i) in npsLine" :key="i" class="text-xs" style="color:#9C998F">{{ p.label }}</span>
            </div>
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
              <div class="w-8 h-9 rounded flex items-center justify-center flex-shrink-0" style="background:#E6F4EA">
                <i class="pi pi-file-excel text-sm" style="color:#1A8049"></i>
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
          <h2 class="font-bold text-sm mb-4" style="color:#21201C;font-family:Montserrat,sans-serif">Répartition des sentiments</h2>
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
const stats = ref({})
const npsSummary = ref([])
const npsSeries = ref({})
const dailyCounts = ref([])

const periodLabel = computed(() => {
  const d = new Date()
  return d.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })
})

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
// Série NPS à plat (tous types, triée par date)
const npsLine = computed(() => {
  const pts = []
  Object.values(npsSeries.value).forEach(arr => arr.forEach(p => pts.push({ date: new Date(p.date), nps: p.nps })))
  pts.sort((a, b) => a.date - b.date)
  return pts.map(p => ({ nps: p.nps, label: p.date.toLocaleDateString('fr-FR', { month: 'short' }) }))
})
const npsSpark = computed(() => npsLine.value.map(p => p.nps + 100))
const npsTrend = computed(() => npsLine.value.length > 1 ? Math.round(npsLine.value[npsLine.value.length-1].nps - npsLine.value[0].nps) : null)

// Courbe NPS (échelle -100..100 affichée 0..100 via (nps+100)/2)
const W = 560, H = 190, PADL = 8, PADR = 8, PADT = 10, PADB = 10
function yAt(pct) { return PADT + (1 - pct/100) * (H - PADT - PADB) }
const npsPts = computed(() => {
  const n = npsLine.value.length
  return npsLine.value.map((p, i) => ({
    x: PADL + (n === 1 ? 0.5 : i/(n-1)) * (W - PADL - PADR),
    y: yAt((p.nps + 100) / 2),
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
const areaPath = computed(() => npsPts.value.length < 2 ? '' : `${linePath.value} L${W-PADR},${H-PADB} L${PADL},${H-PADB} Z`)

function npsColor(n) { return n >= 50 ? '#21A05A' : n >= 0 ? '#B7791F' : '#D4452C' }
function formatNum(n) { return (n || 0).toLocaleString('fr-FR') }
function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR', { day:'2-digit', month:'short', year:'numeric' }) }

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
