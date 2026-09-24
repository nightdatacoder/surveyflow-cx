<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="font-semibold text-gray-700">Modèles de traitement</h2>
    </div>

    <div v-if="!templates.length" class="bg-white rounded-xl shadow-sm p-10 text-center text-gray-400">
      <i class="pi pi-bookmark text-4xl block mb-3"></i>
      <p>Aucun modèle sauvegardé</p>
      <p class="text-sm mt-1">Configurez un fichier puis cliquez sur "Sauvegarder comme modèle"</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div v-for="t in templates" :key="t.id" class="bg-white rounded-xl shadow-sm p-5 hover:shadow-md transition-shadow">
        <div class="flex items-start justify-between mb-3">
          <div class="w-10 h-10 rounded-lg flex items-center justify-center flex-shrink-0" style="background:#FFCC0030">
            <i class="pi pi-bookmark text-sm" style="color:#854d0e"></i>
          </div>
          <button v-if="canDelete(t)" @click="deleteTemplate(t.id)"
            class="text-gray-300 hover:text-red-500 transition-colors" title="Supprimer ce modèle">
            <i class="pi pi-trash text-xs"></i>
          </button>
        </div>
        <h3 class="font-semibold text-gray-700">{{ t.name }}</h3>
        <span class="inline-block mt-1 px-2 py-0.5 text-xs rounded-md font-semibold" style="background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB">{{ t.survey_type || 'Générique' }}</span>
        <div class="mt-3 space-y-1 text-xs text-gray-500">
          <p><i class="pi pi-tag mr-1"></i>{{ Object.keys(t.column_mapping || {}).length }} colonnes mappées</p>
          <p><i class="pi pi-times-circle mr-1"></i>{{ (t.columns_to_drop || []).length }} colonnes supprimées</p>
          <p><i class="pi pi-user mr-1"></i>{{ t.created_by_name }}</p>
        </div>
        <p class="text-xs text-gray-400 mt-3">{{ formatDate(t.created_at) }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import api from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'
import { useToast } from 'primevue/usetoast'

const templates = ref([])
const auth = useAuthStore()
const toast = useToast()
function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR') }

// Seul le créateur du modèle ou un admin peut le supprimer
function canDelete(t) {
  return auth.user?.role === 'ADMIN' || t.created_by === auth.user?.id
}

async function deleteTemplate(id) {
  if (!confirm('Supprimer ce modèle ? Le type d\'enquête associé disparaîtra aussi.')) return
  try {
    await api.delete(`/imports/templates/${id}/`)
    templates.value = templates.value.filter(t => t.id !== id)
  } catch (e) {
    // Modèle de base : le serveur demande une confirmation explicite (409)
    if (e.response?.status === 409) {
      if (confirm(`⚠️ ${e.response.data.warning}`)) {
        try {
          await api.delete(`/imports/templates/${id}/?confirm=true`)
          templates.value = templates.value.filter(t => t.id !== id)
          toast.add({ severity: 'warn', summary: 'Modèle de base supprimé',
            detail: 'Relancez setup_templates.py pour le restaurer si besoin.', life: 6000 })
        } catch (e2) {
          toast.add({ severity: 'error', summary: 'Erreur', detail: e2.response?.data?.error || 'Suppression impossible.', life: 5000 })
        }
      }
      return
    }
    toast.add({ severity: 'error', summary: 'Suppression refusée',
      detail: e.response?.data?.error || 'Seul le créateur ou un admin peut supprimer ce modèle.', life: 5000 })
  }
}

onMounted(async () => {
  const { data } = await api.get('/imports/templates/').catch(() => ({ data: [] }))
  templates.value = data.results || data
})
</script>
