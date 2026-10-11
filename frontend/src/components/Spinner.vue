<template>
  <div class="flex flex-col items-center justify-center gap-3" :style="`min-height:${minHeight}`">
    <svg class="animate-spin" :width="size" :height="size" viewBox="0 0 24 24" fill="none">
      <circle cx="12" cy="12" r="10" stroke="#EFEDE6" stroke-width="3"/>
      <path d="M12 2a10 10 0 0110 10" stroke="#FFCC00" stroke-width="3" stroke-linecap="round"/>
    </svg>
    <p v-if="label" class="text-sm" style="color:#9C998F">{{ label }}</p>
  </div>
</template>
<script setup>
defineProps({
  label: { type: String, default: '' },
  size: { type: [Number, String], default: 30 },
  minHeight: { type: String, default: 'auto' },
})
</script>
