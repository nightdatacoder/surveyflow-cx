<template>
  <div class="bg-white rounded-xl p-4" style="border:1px solid var(--border)">
    <p class="text-xs font-semibold truncate mb-2" style="color:var(--text-secondary)" :title="metric.column">
      {{ metric.column }}
    </p>
    <div class="flex items-center gap-4">
      <!-- Jauge demi-cercle -->
      <svg width="92" height="56" viewBox="0 0 100 60" class="flex-shrink-0">
        <path d="M8 54 A 42 42 0 0 1 92 54" fill="none" stroke="#EFEDE6" stroke-width="9" stroke-linecap="round"/>
        <path d="M8 54 A 42 42 0 0 1 92 54" fill="none" :stroke="npsColor" stroke-width="9"
          stroke-linecap="round" :stroke-dasharray="arc" :stroke-dashoffset="arcOffset"
          style="transition:stroke-dashoffset 0.6s ease"/>
        <text x="50" y="48" text-anchor="middle" style="font-size:21px;font-weight:800;font-family:Montserrat,sans-serif"
          :fill="npsColor">{{ metric.nps > 0 ? '+' : '' }}{{ metric.nps }}</text>
      </svg>
      <div class="flex-1 min-w-0 space-y-1">
        <div class="flex items-center justify-between text-xs">
          <span style="color:var(--text-secondary)">Promoteurs</span>
          <span class="font-bold" style="color:#21A05A">{{ metric.promoters_pct }}%</span>
        </div>
        <div class="flex items-center justify-between text-xs">
          <span style="color:var(--text-secondary)">Passifs</span>
          <span class="font-bold" style="color:#9C998F">{{ metric.passives_pct }}%</span>
        </div>
        <div class="flex items-center justify-between text-xs">
          <span style="color:var(--text-secondary)">Détracteurs</span>
          <span class="font-bold" style="color:#D4452C">{{ metric.detractors_pct }}%</span>
        </div>
      </div>
    </div>
    <!-- Barre empilée -->
    <div class="flex h-2 rounded-full overflow-hidden mt-3" style="background:#EFEDE6">
      <div :style="`width:${metric.detractors_pct}%;background:#D4452C`"></div>
      <div :style="`width:${metric.passives_pct}%;background:#D5D2C8`"></div>
      <div :style="`width:${metric.promoters_pct}%;background:#21A05A`"></div>
    </div>
    <p class="text-xs mt-2" style="color:var(--text-muted)">
      Note moyenne {{ metric.avg }}/10 · {{ metric.total }} réponses
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({ metric: Object })

// NPS va de -100 à +100. La jauge couvre un demi-cercle (longueur arc ≈ 132).
const ARC_LEN = 132
const arc = `${ARC_LEN} ${ARC_LEN}`
const arcOffset = computed(() => {
  const pct = (props.metric.nps + 100) / 200  // 0..1
  return ARC_LEN * (1 - pct)
})
const npsColor = computed(() => {
  const n = props.metric.nps
  if (n >= 50) return '#21A05A'
  if (n >= 0) return '#B7791F'
  return '#D4452C'
})
</script>
