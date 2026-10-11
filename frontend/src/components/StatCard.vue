<template>
  <div class="bg-white rounded-2xl p-5 flex items-center gap-4 stat-card">
    <div class="w-12 h-12 rounded-xl flex items-center justify-center flex-shrink-0"
         style="background:linear-gradient(135deg,#FFF7DA 0%,#FFE7A0 100%);border:1px solid #F3E4A4">
      <i :class="`pi ${icon} text-lg`" style="color:#A9790A"></i>
    </div>
    <div class="min-w-0">
      <p class="text-2xl font-black leading-none" style="color:#21201C;font-family:Montserrat,sans-serif">{{ value }}</p>
      <p class="text-xs mt-1.5" style="color:#9C998F">{{ label }}</p>
    </div>
  </div>
</template>
<script setup>
defineProps({ label: String, value: [String, Number], icon: String, color: String, textColor: String })
</script>
<style scoped>
.stat-card { transition: transform .2s ease, box-shadow .2s ease; }
.stat-card:hover { transform: translateY(-2px); box-shadow: 0 14px 30px -12px rgba(28,27,24,.20) !important; }
</style>
