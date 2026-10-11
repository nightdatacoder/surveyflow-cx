<template>
  <div class="rounded-2xl p-4 sm:p-5 metric-card" :style="`background:${t.bg};border:1px solid ${t.border}`">
    <div class="flex items-center justify-between mb-3">
      <div class="w-11 h-11 rounded-full flex items-center justify-center flex-shrink-0" :style="`background:${t.iconBg}`">
        <i :class="`pi ${icon}`" :style="`color:${t.iconColor};font-size:18px`"></i>
      </div>
      <svg v-if="spark && spark.length > 1" width="68" height="32" viewBox="0 0 68 32" preserveAspectRatio="none" class="flex-shrink-0">
        <template v-if="type === 'bar'">
          <rect v-for="(v, i) in spark" :key="i" :x="i * (68 / spark.length) + 1" :y="32 - barH(v)"
            :width="Math.max(68 / spark.length - 2.5, 2)" :height="barH(v)" :fill="t.accent" rx="1.5" opacity="0.85"/>
        </template>
        <template v-else>
          <polyline :points="linePts" fill="none" :stroke="t.accent" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"/>
        </template>
      </svg>
    </div>
    <p class="text-xs font-medium" :style="`color:${t.label}`">{{ label }}</p>
    <p class="text-2xl font-black mt-0.5 leading-none" style="color:#21201C;font-family:Montserrat,sans-serif">{{ value }}</p>
    <div v-if="trend !== null && trend !== undefined" class="flex items-center gap-1 mt-2 text-xs font-bold"
         :style="`color:${(invertTrend ? -trend : trend) >= 0 ? '#21A05A' : '#D4452C'}`">
      <svg width="11" height="11" viewBox="0 0 24 24" fill="none">
        <polyline v-if="trend >= 0" points="4 14 10 8 14 12 20 6" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
        <polyline v-else points="4 10 10 16 14 12 20 18" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
      </svg>
      {{ trend >= 0 ? '+' : '' }}{{ trend }}{{ suffix }}
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
const props = defineProps({
  label: String, value: [String, Number], icon: String,
  tone: { type: String, default: 'neutral' },
  trend: { type: Number, default: null },
  suffix: { type: String, default: '%' },
  invertTrend: { type: Boolean, default: false },
  spark: { type: Array, default: () => [] },
  type: { type: String, default: 'bar' },
})

const TONES = {
  yellow:  { bg:'#FFF9E6', border:'#F3E79F', iconBg:'#FFE9A3', iconColor:'#A9790A', accent:'#E9A800', label:'#8A6D15' },
  green:   { bg:'#EAF7EF', border:'#C3E7D1', iconBg:'#CFEEDA', iconColor:'#1A8049', accent:'#21A05A', label:'#1A6B41' },
  red:     { bg:'#FDEDED', border:'#F6CBCB', iconBg:'#F8D7D7', iconColor:'#C13C27', accent:'#D4452C', label:'#9C3322' },
  neutral: { bg:'#F7F6F2', border:'#E5E3DB', iconBg:'#EFEDE6', iconColor:'#6E6B63', accent:'#9C998F', label:'#6E6B63' },
}
const t = computed(() => TONES[props.tone] || TONES.neutral)

const max = computed(() => Math.max(...props.spark, 1))
function barH(v) { return Math.max((v / max.value) * 30, 2) }
const linePts = computed(() => {
  const n = props.spark.length
  return props.spark.map((v, i) => `${i * (68 / (n - 1))},${32 - (v / max.value) * 28 - 2}`).join(' ')
})
</script>

<style scoped>
.metric-card { transition: transform .2s ease, box-shadow .2s ease; }
.metric-card:hover { transform: translateY(-2px); box-shadow: 0 14px 30px -12px rgba(28,27,24,.16); }
</style>
