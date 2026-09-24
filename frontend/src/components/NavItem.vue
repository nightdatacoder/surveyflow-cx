<template>
  <router-link :to="to" class="nav-item" :class="{ active: isActive }">
    <span class="nav-icon"><slot name="icon" /></span>
    <span class="text-xs" style="font-family:Montserrat,sans-serif">{{ label }}</span>
    <span v-if="isActive" class="ml-auto w-1.5 h-1.5 rounded-full flex-shrink-0" style="background:#FFCC00"></span>
  </router-link>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute } from 'vue-router'
const props = defineProps({ to: String, label: String })
const route = useRoute()
const isActive = computed(() => route.path === props.to || route.path.startsWith(props.to + '/'))
</script>

<style scoped>
/* Bordure toujours présente (transparente) : aucun décalage au survol/actif */
.nav-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px 10px;
  border-radius: 8px;
  font-weight: 500;
  color: var(--sidebar-text);
  border: 1px solid transparent;
  transition: background-color 0.15s ease, color 0.15s ease, border-color 0.15s ease;
}
.nav-item:hover {
  color: #E8E6DF;
  background: rgba(255, 255, 255, 0.04);
}
.nav-item.active {
  font-weight: 700;
  color: #F5F4EF;
  background: var(--sidebar-active);
  border-color: #38362F;
}
.nav-icon {
  flex-shrink: 0;
  color: #7A776E;
  transition: color 0.15s ease;
}
.nav-item:hover .nav-icon { color: #E8E6DF; }
.nav-item.active .nav-icon { color: #FFCC00; }
</style>
