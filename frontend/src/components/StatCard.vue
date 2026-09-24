<template>
  <div class="bg-white rounded-xl p-5 flex items-center gap-4" style="border:1px solid var(--border)">
    <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0"
         style="background:#F5F4EF;border:1px solid #E5E3DB">
      <i :class="`pi ${icon} text-base`" style="color:#6E6B63"></i>
    </div>
    <div>
      <p class="text-2xl font-bold" style="color:#21201C;font-family:Montserrat,sans-serif">{{ value }}</p>
      <p class="text-xs mt-0.5" style="color:#9C998F">{{ label }}</p>
    </div>
  </div>
</template>
<script setup>
defineProps({ label: String, value: [String, Number], icon: String, color: String, textColor: String })
</script>
