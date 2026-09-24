<template>
  <button @click="download" :disabled="loading"
    class="px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 flex items-center gap-2"
    :style="primary ? 'background:#FFCC00;color:#1F2937' : 'background:#F3F4F6;color:#4B5563'"
    :class="loading ? 'opacity-60 cursor-not-allowed' : 'hover:opacity-85 hover:-translate-y-px'">
    <i v-if="loading" class="pi pi-spin pi-spinner text-xs"></i>
    <i v-else class="pi pi-download text-xs"></i>
    {{ label }}
  </button>
</template>
<script setup>
import { ref } from 'vue'
import { useToast } from 'primevue/usetoast'
import api from '@/composables/useApi'

const props = defineProps({ fileId: [String, Number], mode: String, format: String, label: String, primary: Boolean })
const loading = ref(false)
const toast = useToast()

async function download() {
  loading.value = true
  try {
    const { data, headers } = await api.post('/exports/', {
      file_id: props.fileId, format: props.format, mode: props.mode
    }, { responseType: 'blob' })

    const cd = headers['content-disposition'] || ''
    const match = cd.match(/filename="([^"]+)"|filename=([^;]+)/)
    const filename = (match && (match[1] || match[2]))?.trim() || `export.${props.format}`

    const url = URL.createObjectURL(new Blob([data]))
    const a = document.createElement('a')
    a.href = url; a.download = filename; a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    // La réponse d'erreur est un blob : on la lit pour afficher le vrai message
    let detail = 'Téléchargement impossible.'
    try { detail = JSON.parse(await e.response?.data?.text())?.error || detail } catch {}
    toast.add({ severity: 'error', summary: 'Export refusé', detail, life: 5000 })
  }
  finally { loading.value = false }
}
</script>
