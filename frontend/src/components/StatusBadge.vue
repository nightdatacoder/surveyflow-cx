<template>
  <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-medium whitespace-nowrap"
        style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB">
    <span class="w-1.5 h-1.5 rounded-full flex-shrink-0" :style="`background:${dot}`"></span>
    {{ label }}
  </span>
</template>
<script setup>
import { computed } from 'vue'
const props = defineProps({ status: String })
const MAP = {
  UPLOADED:  { label: 'Uploadé',    dot: '#9C998F' },
  ANALYZING: { label: 'Analyse…',   dot: '#9C998F' },
  ANALYZED:  { label: 'Analysé',    dot: '#9C998F' },
  CLEANING:  { label: 'Nettoyage…', dot: '#FFCC00' },
  CLEANED:   { label: 'Nettoyé',    dot: '#FFCC00' },
  JOINED:    { label: 'Enrichi',    dot: '#21A05A' },
  EXPORTED:  { label: 'Exporté',    dot: '#21A05A' },
  ERROR:     { label: 'Erreur',     dot: '#D4452C' },
}
const entry = computed(() => MAP[props.status] || { label: props.status, dot: '#9C998F' })
const label = computed(() => entry.value.label)
const dot = computed(() => entry.value.dot)
</script>
