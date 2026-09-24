<template>
  <button @click="$emit('select')"
    class="flex-1 p-3 rounded-xl border-2 text-left transition-all"
    :class="selected ? 'border-yellow-400 bg-yellow-50' : 'border-gray-200 hover:border-gray-300'">
    <p class="font-semibold text-sm" :class="selected ? 'text-yellow-800' : 'text-gray-700'">{{ type.label }}</p>
    <p class="text-xs mt-0.5" :class="selected ? 'text-yellow-700' : 'text-gray-400'">{{ type.desc }}</p>
  </button>
</template>
<script setup>
defineProps({ type: Object, selected: Boolean })
defineEmits(['select'])
</script>
