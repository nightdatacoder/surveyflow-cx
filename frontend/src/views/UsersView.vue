<template>
  <div class="space-y-4">
    <div class="flex items-center justify-between">
      <h2 class="font-semibold text-gray-700">Gestion des utilisateurs</h2>
      <button @click="showCreate = true" class="px-4 py-2 rounded-lg text-sm font-semibold" style="background:#23221E;color:#F5F4EF">
        <i class="pi pi-plus mr-1"></i>Nouvel utilisateur
      </button>
    </div>

    <div class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full text-sm">
        <thead class="bg-gray-50">
          <tr class="text-left text-xs text-gray-500">
            <th class="px-4 py-3 font-semibold">Utilisateur</th>
            <th class="px-4 py-3 font-semibold">Identifiant</th>
            <th class="px-4 py-3 font-semibold">Rôle</th>
            <th class="px-4 py-3 font-semibold">Département</th>
            <th class="px-4 py-3 font-semibold">Statut</th>
            <th class="px-4 py-3 font-semibold">Créé le</th>
            <th class="px-4 py-3"></th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-50">
          <tr v-for="u in users" :key="u.id" class="hover:bg-gray-50">
            <td class="px-4 py-3">
              <div class="flex items-center gap-3">
                <div class="w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold flex-shrink-0"
                     style="background:#FFCC00;color:#23221E">
                  {{ initials(u) }}
                </div>
                <span class="font-medium text-gray-700">{{ u.full_name || u.username }}</span>
              </div>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ u.username }}</td>
            <td class="px-4 py-3">
              <span class="px-2 py-0.5 rounded-full text-xs font-semibold"
                    :style="roleStyle(u.role)">{{ roleLabel(u.role) }}</span>
            </td>
            <td class="px-4 py-3 text-gray-500">{{ u.department || '—' }}</td>
            <td class="px-4 py-3">
              <span :class="`px-2 py-0.5 rounded-full text-xs ${u.is_active ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-600'}`">
                {{ u.is_active ? 'Actif' : 'Inactif' }}
              </span>
            </td>
            <td class="px-4 py-3 text-xs text-gray-400">{{ formatDate(u.created_at) }}</td>
            <td class="px-4 py-3">
              <div class="flex items-center gap-3 justify-end">
                <button @click="openReset(u)" class="text-xs text-gray-400 hover:text-gray-700" title="Définir un nouveau mot de passe">
                  <i class="pi pi-key mr-1" style="font-size:10px"></i>Mot de passe
                </button>
                <button v-if="u.id !== auth.user?.id" @click="toggleActive(u)" class="text-xs text-gray-400 hover:text-gray-600">
                  {{ u.is_active ? 'Désactiver' : 'Activer' }}
                </button>
                <span v-else class="text-xs" style="color:#D5D2C8">Vous</span>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Reset password modal -->
    <div v-if="resetTarget" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-sm mx-4">
        <h3 class="font-semibold text-gray-700 mb-1">Nouveau mot de passe</h3>
        <p class="text-xs mb-4" style="color:#9C998F">
          Pour <strong>{{ resetTarget.full_name || resetTarget.username }}</strong>.
          Les mots de passe sont chiffrés : impossible d'afficher l'actuel, mais vous pouvez en définir un nouveau.
        </p>
        <input v-model="resetPassword" type="text" placeholder="Nouveau mot de passe (min. 6 caractères)" class="input-field w-full" />
        <div class="flex gap-3 pt-4">
          <button type="button" @click="resetTarget = null" class="flex-1 py-2 rounded-lg border text-sm text-gray-600">Annuler</button>
          <button @click="submitReset" :disabled="resetPassword.length < 6"
            class="flex-1 py-2 rounded-lg text-sm font-semibold disabled:opacity-40" style="background:#23221E;color:#F5F4EF">
            Réinitialiser
          </button>
        </div>
      </div>
    </div>

    <!-- Create modal -->
    <div v-if="showCreate" class="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <div class="bg-white rounded-2xl p-6 w-full max-w-md mx-4">
        <h3 class="font-semibold text-gray-700 mb-4">Créer un utilisateur</h3>
        <form @submit.prevent="createUser" class="space-y-3">
          <div class="grid grid-cols-2 gap-3">
            <input v-model="newUser.first_name" placeholder="Prénom" class="input-field" />
            <input v-model="newUser.last_name" placeholder="Nom" class="input-field" />
          </div>
          <input v-model="newUser.username" placeholder="Identifiant *" class="input-field w-full" />
          <input v-model="newUser.email" type="email" placeholder="Email (facultatif)" class="input-field w-full" />
          <input v-model="newUser.password" type="text" placeholder="Mot de passe * (8 caractères min.)" class="input-field w-full" />
          <p class="text-xs" style="color:#9C998F">L'identifiant et le mot de passe sont obligatoires. Communiquez-les à la personne.</p>
          <select v-model="newUser.role" class="input-field w-full">
            <option value="AGENT">Agent CX</option>
            <option value="MANAGER">Manager CX</option>
            <option value="ADMIN">Administrateur</option>
          </select>
          <input v-model="newUser.department" placeholder="Département" class="input-field w-full" />
          <div class="flex gap-3 pt-2">
            <button type="button" @click="showCreate = false" class="flex-1 py-2 rounded-lg border text-sm text-gray-600">Annuler</button>
            <button type="submit" :disabled="creating"
              class="flex-1 py-2 rounded-lg text-sm font-semibold flex items-center justify-center gap-2 disabled:opacity-60"
              style="background:#23221E;color:#F5F4EF">
              <i v-if="creating" class="pi pi-spin pi-spinner text-xs"></i>
              {{ creating ? 'Création…' : 'Créer' }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useToast } from 'primevue/usetoast'
import api from '@/composables/useApi'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const toast = useToast()
const users = ref([])
const showCreate = ref(false)
const newUser = ref({ first_name: '', last_name: '', username: '', email: '', password: '', role: 'AGENT', department: '' })
const resetTarget = ref(null)
const resetPassword = ref('')
const creating = ref(false)

function openReset(u) { resetTarget.value = u; resetPassword.value = '' }

async function submitReset() {
  try {
    const { data } = await api.post(`/auth/users/${resetTarget.value.id}/set_password/`, { new_password: resetPassword.value })
    toast.add({ severity: 'success', summary: 'Mot de passe modifié', detail: data.message, life: 4000 })
    resetTarget.value = null
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Erreur', detail: e.response?.data?.error || 'Modification impossible.', life: 5000 })
  }
}

function initials(u) { return u.full_name ? u.full_name.split(' ').map(w => w[0]).join('').substring(0, 2).toUpperCase() : u.username[0].toUpperCase() }
function formatDate(d) { return new Date(d).toLocaleDateString('fr-FR') }
function roleLabel(r) { return { ADMIN: 'Administrateur', MANAGER: 'Manager CX', AGENT: 'Agent CX' }[r] || r }
function roleStyle(r) { return { ADMIN: 'background:#23221E;color:#FFCC00', MANAGER: 'background:#F5F4EF;color:#21201C;border:1px solid #E5E3DB', AGENT: 'background:#F5F4EF;color:#6E6B63;border:1px solid #E5E3DB' }[r] || '' }

async function toggleActive(u) {
  await api.patch(`/auth/users/${u.id}/`, { is_active: !u.is_active })
  u.is_active = !u.is_active
}

// Transforme les erreurs DRF ({"password":["..."], "username":["..."]}) en texte lisible
function readableError(data) {
  if (!data) return "Vérifiez que le serveur est démarré et réessayez."
  if (typeof data === 'string') return data
  const map = { password: 'Mot de passe', username: 'Identifiant', email: 'Email', role: 'Rôle' }
  return Object.entries(data)
    .map(([field, msgs]) => `${map[field] || field} : ${Array.isArray(msgs) ? msgs.join(' ') : msgs}`)
    .join('\n')
}

async function createUser() {
  // Validations claires AVANT l'envoi
  if (!newUser.value.username.trim()) {
    toast.add({ severity: 'warn', summary: 'Identifiant requis', detail: 'Saisissez un identifiant.', life: 4000 })
    return
  }
  if (newUser.value.password.length < 8) {
    toast.add({ severity: 'warn', summary: 'Mot de passe trop court', detail: 'Le mot de passe doit faire au moins 8 caractères.', life: 4000 })
    return
  }
  creating.value = true
  try {
    const { data } = await api.post('/auth/users/', newUser.value)
    users.value.unshift(data)
    showCreate.value = false
    newUser.value = { first_name: '', last_name: '', username: '', email: '', password: '', role: 'AGENT', department: '' }
    toast.add({ severity: 'success', summary: 'Utilisateur créé', detail: `${data.username} peut maintenant se connecter.`, life: 4000 })
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Création impossible', detail: readableError(e.response?.data), life: 6000 })
  } finally {
    creating.value = false
  }
}

onMounted(async () => {
  const { data } = await api.get('/auth/users/').catch(() => ({ data: [] }))
  users.value = data.results || data
})
</script>

<style>
.input-field { @apply px-3 py-2 border border-gray-200 rounded-lg text-sm focus:outline-none focus:border-yellow-400; }
</style>
