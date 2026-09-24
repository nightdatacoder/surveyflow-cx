<template>
  <div class="space-y-5">
    <!-- Stats cards -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <StatCard label="Rapports créés" :value="stats.total_reports" icon="pi-file" />
      <StatCard label="Lignes traitées" :value="formatNum(stats.total_rows)" icon="pi-database" />
      <StatCard label="Ce mois" :value="stats.this_month || '—'" icon="pi-calendar" />
      <StatCard label="Fichiers prêts" :value="activeFiles" icon="pi-check-circle" />
    </div>

    <!-- Activity chart -->
    <div class="bg-white rounded-xl p-5" style="border:1px solid var(--border)">
      <div class="flex items-center justify-between mb-1">
        <h2 class="font-bold text-sm" style="color:#21201C;font-family:Montserrat,sans-serif">Activité des 14 derniers jours</h2>
        <span class="text-xs" style="color:#9C998F">{{ chartTotal }} import(s)</span>
      </div>
      <svg :viewBox="`0 0 ${W} ${H}`" class="w-full mt-2" style="height:auto;max-height:170px">
        <defs>
          <linearGradient id="areaFill" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#FFCC00" stop-opacity="0.3"/>
            <stop offset="100%" stop-color="#FFCC00" stop-opacity="0"/>
          </linearGradient>
        </defs>
        <!-- Lignes de repère horizontales -->
        <line v-for="g in 3" :key="g" :x1="PAD" :x2="W - PAD"
          :y1="PAD + (g - 1) * (H - PAD * 2) / 2" :y2="PAD + (g - 1) * (H - PAD * 2) / 2"
          stroke="#EFEDE6" stroke-width="1"/>
        <path :d="areaPath" fill="url(#areaFill)"/>
        <path :d="linePath" fill="none" stroke="#23221E" stroke-width="1.5" stroke-linejoin="round" stroke-linecap="round"/>
        <g v-for="(p, i) in points" :key="i">
          <circle v-if="dailyCounts[i] > 0" :cx="p.x" :cy="p.y" r="3.5" fill="#FFCC00" stroke="#23221E" stroke-width="1.5"/>
          <text v-if="dailyCounts[i] > 0" :x="p.x" :y="p.y - 9" text-anchor="middle"
            style="font-size:10px;font-weight:700;fill:#21201C;font-family:Montserrat,sans-serif">{{ dailyCounts[i] }}</text>
        </g>
      </svg>
      <div class="flex justify-between mt-1">
        <span class="text-xs" style="color:#9C998F">{{ chartLabels[0] }}</span>
        <span class="text-xs" style="color:#9C998F">{{ chartLabels[1] }}</span>
      </div>
    </div>

    <!-- Satisfaction (NPS) par enquête et par période -->
    <div v-if="npsSummary.length" class="bg-white rounded-xl p-5" style="border:1px solid var(--border)">
      <div class="flex items-center justify-between mb-1">
        <h2 class="font-bold text-sm" style="color:#21201C;font-family:Montserrat,sans-serif">Satisfaction client (NPS) par enquête</h2>
      </div>
      <p class="text-xs mb-4" style="color:var(--text-muted)">
        Le NPS va de −100 à +100. Au-dessus de 0 c'est bon, au-dessus de +50 c'est excellent. La flèche compare à la période précédente.
      </p>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
        <div v-for="s in npsSummary" :key="s.survey_type"
          class="p-4 rounded-xl flex items-center gap-4" style="background:#FAF9F5;border:1px solid var(--border)">
          <!-- Score + tendance -->
          <div class="flex-shrink-0" style="width:96px">
            <p class="text-xs font-semibold truncate" style="color:var(--text-secondary)">{{ s.survey_type }}</p>
            <div class="flex items-baseline gap-1.5 mt-0.5">
              <span class="text-2xl font-black" :style="`color:${npsColor(s.latest_nps)};font-family:Montserrat,sans-serif`">
                {{ s.latest_nps > 0 ? '+' : '' }}{{ s.latest_nps }}
              </span>
            </div>
            <span v-if="s.delta !== null" class="text-xs font-bold inline-flex items-center"
              :style="`color:${s.delta >= 0 ? '#21A05A' : '#D4452C'}`">
              <svg width="10" height="10" viewBox="0 0 24 24" fill="none" class="mr-0.5">
                <polyline v-if="s.delta >= 0" points="6 15 12 9 18 15" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
                <polyline v-else points="6 9 12 15 18 9" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
              </svg>
              {{ s.delta >= 0 ? '+' : '' }}{{ s.delta }} vs période précédente
            </span>
            <span v-else class="text-xs" style="color:var(--text-muted)">1ère période</span>
          </div>
          <!-- Mini-courbe des périodes -->
          <div class="flex-1 min-w-0">
            <svg :viewBox="`0 0 ${sparkW} ${sparkH}`" class="w-full" style="height:48px" preserveAspectRatio="none">
              <line :x1="0" :x2="sparkW" :y1="npsToY(0)" :y2="npsToY(0)" stroke="#D5D2C8" stroke-width="0.8" stroke-dasharray="2 2"/>
              <polyline :points="sparkPoints(s.survey_type)" fill="none" :stroke="npsColor(s.latest_nps)" stroke-width="2" stroke-linejoin="round" stroke-linecap="round"/>
              <circle v-for="(p, i) in sparkDots(s.survey_type)" :key="i" :cx="p.x" :cy="p.y" r="2.5" :fill="npsColor(s.latest_nps)"/>
            </svg>
            <p class="text-xs mt-0.5 text-center" style="color:var(--text-muted)">{{ s.count }} période(s) suivie(s)</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Two columns -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-5">
      <!-- Recent files -->
      <div class="lg:col-span-2 bg-white rounded-xl p-5" style="border:1px solid var(--border)">
        <div class="flex items-center justify-between mb-4">
          <h2 class="font-bold text-sm" style="color:#21201C;font-family:Montserrat,sans-serif">Fichiers récents</h2>
          <router-link to="/import" class="text-xs font-semibold px-3 py-1.5 rounded-lg"
            style="background:#FFCC00;color:#23221E">+ Importer</router-link>
        </div>
        <div v-if="!stats.recent_files?.length" class="text-center py-10" style="color:#9C998F">
          <i class="pi pi-inbox text-3xl block mb-2"></i>
          Aucun fichier importé pour l'instant
        </div>
        <div v-else class="space-y-1">
          <div v-for="f in stats.recent_files" :key="f.id"
            class="flex items-center gap-3 p-3 rounded-lg hover:bg-[#FAF9F5] transition-colors">
            <div class="w-9 h-9 rounded-lg flex items-center justify-center flex-shrink-0"
                 style="background:#F5F4EF;border:1px solid #E5E3DB">
              <i class="pi pi-file-excel text-sm" style="color:#6E6B63"></i>
            </div>
            <div class="flex-1 min-w-0">
              <p class="text-sm font-medium truncate" style="color:#21201C">{{ f.name }}</p>
              <p class="text-xs" style="color:#9C998F">{{ f.project }} · {{ f.rows.toLocaleString() }} lignes · {{ formatDate(f.date) }}</p>
            </div>
            <StatusBadge :status="f.status" />
          </div>
        </div>
      </div>

      <!-- Status breakdown -->
      <div class="bg-white rounded-xl p-5" style="border:1px solid var(--border)">
        <h2 class="font-bold text-sm mb-4" style="color:#21201C;font-family:Montserrat,sans-serif">Répartition par statut</h2>
        <div class="space-y-3">
          <div v-for="(count, status) in stats.status_breakdown" :key="status">
            <div class="flex justify-between text-xs mb-1" style="color:#6E6B63">
              <span>{{ statusLabel(status) }}</span>
              <span class="font-semibold" style="color:#21201C">{{ count }}</span>
            </div>
            <div class="w-full rounded-full h-1.5" style="background:#EFEDE6">
              <div class="h-1.5 rounded-full transition-all"
                   :style="`width:${Math.min(count/Math.max(stats.total_reports,1)*100,100)}%;background:#23221E`"></div>
            </div>
          </div>
        </div>

        <!-- Manager/Admin : répartition par type en % -->
        <div v-if="(auth.isManager || auth.isAdmin) && managerStats" class="mt-5 pt-5" style="border-top:1px solid var(--border)">
          <h3 class="text-xs font-bold uppercase tracking-wide mb-3" style="color:#9C998F">Répartition par projet (équipe)</h3>
          <div v-for="item in typePercents" :key="item.survey_type" class="mb-2.5">
            <div class="flex justify-between text-xs mb-1" style="color:#6E6B63">
              <span>{{ item.survey_type || 'Non défini' }}</span>
              <span class="font-semibold" style="color:#21201C">{{ item.pct }}% · {{ item.count }} fichier(s)</span>
            </div>
            <div class="w-full rounded-full h-1.5" style="background:#EFEDE6">
              <div class="h-1.5 rounded-full transition-all" :style="`width:${item.pct}%;background:#FFCC00`"></div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import api from '@/composables/useApi'
import StatCard from '@/components/StatCard.vue'
import StatusBadge from '@/components/StatusBadge.vue'

const auth = useAuthStore()
const stats = ref({ total_reports: 0, total_rows: 0, recent_files: [], status_breakdown: {} })
const managerStats = ref(null)
const dailyCounts = ref(Array(14).fill(0))
const npsSummary = ref([])
const npsSeries = ref({})

function npsColor(n) { return n >= 50 ? '#21A05A' : n >= 0 ? '#B7791F' : '#D4452C' }

// Mini-courbes NPS par type (échelle fixe -100..+100)
const sparkW = 100, sparkH = 40
function npsToY(nps) { return sparkH - ((nps + 100) / 200) * sparkH }
function sparkDots(type) {
  const pts = npsSeries.value[type] || []
  const n = pts.length
  if (!n) return []
  return pts.map((p, i) => ({
    x: n === 1 ? sparkW / 2 : (i / (n - 1)) * sparkW,
    y: npsToY(p.nps),
  }))
}
function sparkPoints(type) {
  return sparkDots(type).map(p => `${p.x},${p.y}`).join(' ')
}

const activeFiles = computed(() =>
  (stats.value.status_breakdown?.['CLEANED'] || 0) + (stats.value.status_breakdown?.['JOINED'] || 0)
)

// Répartition par type d'enquête en pourcentage (vue manager)
const typePercents = computed(() => {
  const items = managerStats.value?.by_survey_type || []
  const total = items.reduce((a, b) => a + (b.count || 0), 0) || 1
  return items.slice(0, 6).map(i => ({ ...i, pct: Math.round((i.count || 0) / total * 100) }))
})

// Courbe d'activité : imports par jour sur 14 jours (courbe lissée)
const W = 900, H = 150, PAD = 16
const chartTotal = computed(() => dailyCounts.value.reduce((a, b) => a + b, 0))
const points = computed(() => {
  const max = Math.max(...dailyCounts.value, 1)
  const n = dailyCounts.value.length
  return dailyCounts.value.map((v, i) => ({
    x: PAD + (i / (n - 1)) * (W - PAD * 2),
    y: H - PAD - (v / max) * (H - PAD * 2 - 16),
  }))
})
// Courbe de Bézier lissée entre les points (style Claude, pas de cassures)
const linePath = computed(() => {
  const pts = points.value
  if (pts.length < 2) return ''
  let d = `M${pts[0].x},${pts[0].y}`
  for (let i = 1; i < pts.length; i++) {
    const prev = pts[i - 1], curr = pts[i]
    const midX = (prev.x + curr.x) / 2
    d += ` C${midX},${prev.y} ${midX},${curr.y} ${curr.x},${curr.y}`
  }
  return d
})
const areaPath = computed(() =>
  `${linePath.value} L${W - PAD},${H - PAD} L${PAD},${H - PAD} Z`
)
const chartLabels = computed(() => {
  const fmt = d => d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' })
  const today = new Date()
  const start = new Date(today); start.setDate(today.getDate() - 13)
  return [fmt(start), fmt(today)]
})

onMounted(async () => {
  try {
    const { data } = await api.get('/dashboard/agent/')
    stats.value = data
  } catch {}
  if (auth.isManager || auth.isAdmin) {
    try {
      const { data } = await api.get('/dashboard/manager/')
      managerStats.value = data
      stats.value.this_month = data.this_month_reports
    } catch {}
  }
  // Construire la courbe depuis la liste des imports (déjà filtrée par rôle côté serveur)
  try {
    const { data } = await api.get('/imports/files/')
    const files = data?.results || data || []
    const counts = Array(14).fill(0)
    const today = new Date(); today.setHours(0, 0, 0, 0)
    files.forEach(f => {
      const d = new Date(f.created_at); d.setHours(0, 0, 0, 0)
      const diff = Math.round((today - d) / 86400000)
      if (diff >= 0 && diff < 14) counts[13 - diff]++
    })
    dailyCounts.value = counts
  } catch {}
  // Évolution NPS période sur période
  try {
    const { data } = await api.get('/history/reports/nps_evolution/')
    npsSummary.value = data.summary || []
    npsSeries.value = data.series || {}
  } catch {}
})

function formatNum(n) { return (n || 0).toLocaleString('fr-FR') }
function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR', { day: '2-digit', month: 'short' }) }

const STATUS_LABELS = {
  UPLOADED: 'Uploadé', ANALYZED: 'Analysé', CLEANED: 'Nettoyé',
  JOINED: 'Enrichi', EXPORTED: 'Exporté', ERROR: 'Erreur'
}
function statusLabel(s) { return STATUS_LABELS[s] || s }
</script>
