<template>
  <div class="min-h-screen flex" style="background:#FAF9F5">
    <!-- Left panel — branding -->
    <div class="hidden lg:flex flex-col justify-between w-[420px] flex-shrink-0 p-10"
         style="background:#23221E">
      <!-- Logo -->
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-xl flex items-center justify-center font-black text-sm tracking-tight"
             style="background:#FFCC00;color:#23221E;font-family:Montserrat,sans-serif">SF</div>
        <div>
          <p class="text-white font-bold text-sm tracking-tight" style="font-family:Montserrat,sans-serif">SurveyFlow CX</p>
          <p class="text-xs mt-px" style="color:#9C998F">MTN Customer Experience</p>
        </div>
      </div>

      <!-- Center content -->
      <div>
        <div class="w-14 h-14 rounded-2xl flex items-center justify-center mb-6"
             style="background:rgba(255,204,0,.15)">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
            <path d="M9 17H5a2 2 0 01-2-2V5a2 2 0 012-2h11a2 2 0 012 2v3" stroke="#FFCC00" stroke-width="2" stroke-linecap="round"/>
            <path d="M13 13h8m0 0l-3-3m3 3l-3 3" stroke="#FFCC00" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"/>
          </svg>
        </div>
        <h1 class="text-3xl font-black text-white leading-tight mb-4"
            style="font-family:Montserrat,sans-serif;letter-spacing:-.02em">
          Traitez vos<br/>enquêtes en<br/><span style="color:#FFCC00">quelques clics.</span>
        </h1>
        <p class="text-sm leading-relaxed" style="color:#B8B5AC">
          Nettoyage automatique · Jointures intelligentes ·<br/>
          Historisation · Export prêt pour l'analyse
        </p>

        <!-- Feature pills -->
        <div class="flex flex-wrap gap-2 mt-6">
          <span v-for="f in features" :key="f"
            class="px-3 py-1.5 rounded-full text-xs font-semibold"
            style="background:rgba(255,255,255,.08);color:rgba(255,255,255,.7)">
            {{ f }}
          </span>
        </div>
      </div>

      <p class="text-xs" style="color:#7A776E">© 2025 MTN Côte d'Ivoire</p>
    </div>

    <!-- Right panel — form -->
    <div class="flex-1 flex items-center justify-center p-6">
      <div class="w-full max-w-[400px]">
        <!-- Mobile logo -->
        <div class="lg:hidden flex items-center gap-3 mb-8">
          <div class="w-9 h-9 rounded-xl flex items-center justify-center font-black text-xs"
               style="background:#23221E;color:#FFCC00;font-family:Montserrat,sans-serif">SF</div>
          <p class="font-bold text-sm" style="color:#21201C;font-family:Montserrat,sans-serif">SurveyFlow CX</p>
        </div>

        <h2 class="text-2xl font-black mb-1" style="font-family:Montserrat,sans-serif;letter-spacing:-.02em;color:#21201C">
          Connexion
        </h2>
        <p class="text-sm mb-8" style="color:#6E6B63">Bienvenue. Entrez vos identifiants pour continuer.</p>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="block text-xs font-bold mb-1.5 uppercase tracking-wide" style="color:#6E6B63;font-family:Montserrat,sans-serif">
              Identifiant
            </label>
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2" width="15" height="15" viewBox="0 0 24 24" fill="none">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" stroke="#9C998F" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="7" r="4" stroke="#9C998F" stroke-width="2"/>
              </svg>
              <input v-model="form.username" type="text" placeholder="votre.identifiant" required
                class="input-base"
                style="font-family:Montserrat,sans-serif;padding-left:40px" />
            </div>
          </div>

          <!-- Password -->
          <div>
            <div class="flex items-center justify-between mb-1.5">
              <label class="text-xs font-bold uppercase tracking-wide" style="color:#6E6B63;font-family:Montserrat,sans-serif">
                Mot de passe
              </label>
            </div>
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2" width="15" height="15" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="11" width="18" height="11" rx="2" stroke="#9C998F" stroke-width="2"/>
                <path d="M7 11V7a5 5 0 0110 0v4" stroke="#9C998F" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="••••••••" required
                class="input-base" style="font-family:Montserrat,sans-serif;padding-left:40px;padding-right:40px" />
              <button type="button" @click="showPwd = !showPwd"
                class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 transition-colors">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none">
                  <path v-if="!showPwd" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
                  <circle v-if="!showPwd" cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                  <path v-if="showPwd" d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Error -->
          <div v-if="error" class="flex items-center gap-2 p-3 rounded-xl text-sm"
               style="background:#FEF2F2;color:#DC2626;border:1px solid #FECACA">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 8v4m0 4h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
            {{ error }}
          </div>

          <!-- Submit -->
          <button type="submit" :disabled="loading" class="btn-primary w-full flex items-center justify-center gap-2 mt-2"
                  style="font-family:Montserrat,sans-serif;padding:12px;font-size:14px">
            <svg v-if="loading" class="animate-spin" width="16" height="16" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="rgba(0,0,0,.2)" stroke-width="3"/>
              <path d="M12 2a10 10 0 0110 10" stroke="#1A1D23" stroke-width="3" stroke-linecap="round"/>
            </svg>
            {{ loading ? 'Connexion en cours…' : 'Se connecter' }}
          </button>
        </form>

        <p class="text-xs mt-6 text-center" style="color:#9C998F">
          Pas de compte ? Contactez votre administrateur.
        </p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const auth = useAuthStore()
const router = useRouter()
const form = ref({ username: '', password: '' })
const loading = ref(false)
const error = ref('')
const showPwd = ref(false)

const features = ['VOC EBU', 'FTTH', '4G', 'Roaming', 'SurveyMonkey', 'Jointure auto']

async function handleLogin() {
  loading.value = true
  error.value = ''
  try {
    await auth.login(form.value.username, form.value.password)
    router.push('/dashboard')
  } catch (e) {
    error.value = e.response?.data?.detail || 'Identifiants incorrects. Veuillez réessayer.'
  } finally {
    loading.value = false
  }
}
</script>
