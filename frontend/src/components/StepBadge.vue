<template>
  <div class="flex items-center gap-2 flex-shrink-0">
    <div class="w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold transition-all"
         :style="done ? 'background:#23221E;color:#FFCC00' : active ? 'background:#FFCC00;color:#23221E' : 'background:#F5F4EF;color:#9C998F;border:1px solid #E5E3DB'">
      <i v-if="done && icon" :class="`pi ${icon}`" style="font-size:11px"></i>
      <i v-else-if="done" class="pi pi-check" style="font-size:10px"></i>
      <span v-else>{{ n }}</span>
    </div>
    <span class="text-sm font-medium hidden sm:block"
          :style="done || active ? 'color:#21201C' : 'color:#9C998F'">{{ label }}</span>
  </div>
</template>
<script setup>
defineProps({ n: Number, done: Boolean, active: Boolean, label: String, icon: String })
</script>
