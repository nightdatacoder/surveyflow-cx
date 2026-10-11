<template>
  <div class="min-h-screen w-full flex" style="background:#FAF9F5">

    <!-- ===== Panneau gauche : hero (desktop) ===== -->
    <div class="hidden lg:flex flex-col justify-between relative overflow-hidden"
         style="width:46%;max-width:640px;background:#1C1B18">
      <!-- Photo -->
      <img src="/hero.jpg" alt="" class="absolute inset-0 w-full h-full object-cover" style="object-position:center 20%" />
      <!-- Dégradé charbon pour lisibilité -->
      <div class="absolute inset-0" aria-hidden="true"
           style="background:linear-gradient(180deg,rgba(24,23,20,.72) 0%,rgba(24,23,20,.48) 42%,rgba(24,23,20,.97) 100%)"></div>
      <!-- Pattern MTN en filigrane -->
      <div class="absolute inset-0" aria-hidden="true"
           style="background-image:url('/mtn-pattern.png');background-size:130%;background-position:center;opacity:.06;filter:invert(1);mix-blend-mode:screen"></div>
      <!-- Glow jaune chaud -->
      <div class="absolute -bottom-28 -left-20 w-[480px] h-[480px] rounded-full" aria-hidden="true"
           style="background:radial-gradient(circle,rgba(255,204,0,.38) 0%,rgba(255,204,0,0) 66%)"></div>

      <!-- Logo (sans carré) -->
      <div class="relative flex items-center gap-3 p-10">
        <img src="/surveyflow-s.svg" alt="SurveyFlow CX" class="w-11 h-11" style="filter:drop-shadow(0 2px 8px rgba(0,0,0,.4))" />
        <div>
          <p class="text-white font-black text-base tracking-tight leading-none" style="font-family:Montserrat,sans-serif">SurveyFlow CX</p>
          <p class="text-xs mt-1" style="color:#D6D3CA">MTN · Customer Experience</p>
        </div>
      </div>

      <div class="flex-1"></div>

      <!-- Accroche (en bas, sur la zone sombre) -->
      <div class="relative px-10 pb-10">
        <h1 class="font-black text-white leading-[1.08] mb-4"
            style="font-family:Montserrat,sans-serif;letter-spacing:-.03em;font-size:clamp(1.9rem,3.2vw,2.9rem)">
          Transformez vos<br/>enquêtes clients en<br/><span style="color:#FFCC00">décisions.</span>
        </h1>
        <p class="text-sm leading-relaxed max-w-sm mb-5" style="color:#D6D3CA">
          Nettoyage automatique, jointures intelligentes et analyse du NPS —
          sans écrire une ligne de code.
        </p>
        <div class="flex flex-wrap gap-2 max-w-md">
          <span v-for="f in features" :key="f"
            class="px-3 py-1.5 rounded-full text-xs font-semibold"
            style="background:rgba(255,255,255,.12);color:#fff;border:1px solid rgba(255,255,255,.14);backdrop-filter:blur(4px)">
            {{ f }}
          </span>
        </div>
      </div>
    </div>

    <!-- ===== Panneau droit : formulaire ===== -->
    <div class="flex-1 flex items-center justify-center relative px-5 py-8 sm:px-10"
         style="background:linear-gradient(160deg,#FAF9F5 0%,#F1EFE8 100%)">
      <!-- Pattern en fond -->
      <div class="absolute inset-0 pointer-events-none" aria-hidden="true"
           style="background-image:url('/mtn-pattern.png');background-size:135%;background-position:center;opacity:.11"></div>
      <!-- Léger halo jaune en haut à droite -->
      <div class="absolute -top-20 -right-24 w-[380px] h-[380px] rounded-full pointer-events-none" aria-hidden="true"
           style="background:radial-gradient(circle,rgba(255,204,0,.12) 0%,rgba(255,204,0,0) 70%)"></div>

      <!-- Carte -->
      <div class="relative w-full max-w-[430px] bg-white rounded-3xl fade-up"
           style="border:1px solid #EAE7DE;box-shadow:0 24px 60px -20px rgba(28,27,24,.18),0 8px 24px -12px rgba(28,27,24,.10);padding:40px 36px">

        <!-- Logo -->
        <div class="flex items-center gap-2.5 mb-10">
          <img src="/surveyflow-s.svg" alt="" class="w-10 h-10 flex-shrink-0" />
          <div>
            <p class="font-black text-sm leading-none" style="color:#1C1B18;font-family:Montserrat,sans-serif">SurveyFlow CX</p>
            <p class="text-xs mt-1" style="color:#9C998F">MTN · Customer Experience</p>
          </div>
        </div>

        <h2 class="text-2xl font-black mb-2" style="font-family:Montserrat,sans-serif;letter-spacing:-.02em;color:#1C1B18">
          Connexion
        </h2>
        <p class="text-sm mb-8" style="color:#6E6B63">Accédez à votre espace de traitement des enquêtes.</p>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Identifiant -->
          <div>
            <label class="block text-xs font-bold mb-1.5 uppercase tracking-wide" style="color:#6E6B63;font-family:Montserrat,sans-serif">Identifiant</label>
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2" stroke="#9C998F" stroke-width="2" stroke-linecap="round"/>
                <circle cx="12" cy="7" r="4" stroke="#9C998F" stroke-width="2"/>
              </svg>
              <input v-model="form.username" type="text" placeholder="votre.identifiant" required autofocus
                class="input-base" style="font-family:Montserrat,sans-serif;padding-left:42px;height:48px" />
            </div>
          </div>

          <!-- Mot de passe -->
          <div>
            <label class="block text-xs font-bold mb-1.5 uppercase tracking-wide" style="color:#6E6B63;font-family:Montserrat,sans-serif">Mot de passe</label>
            <div class="relative">
              <svg class="absolute left-3.5 top-1/2 -translate-y-1/2" width="16" height="16" viewBox="0 0 24 24" fill="none">
                <rect x="3" y="11" width="18" height="11" rx="2" stroke="#9C998F" stroke-width="2"/>
                <path d="M7 11V7a5 5 0 0110 0v4" stroke="#9C998F" stroke-width="2" stroke-linecap="round"/>
              </svg>
              <input v-model="form.password" :type="showPwd ? 'text' : 'password'" placeholder="••••••••" required
                class="input-base" style="font-family:Montserrat,sans-serif;padding-left:42px;padding-right:42px;height:48px" />
              <button type="button" @click="showPwd = !showPwd" tabindex="-1"
                class="absolute right-3 top-1/2 -translate-y-1/2 transition-colors" style="color:#9C998F">
                <svg width="17" height="17" viewBox="0 0 24 24" fill="none">
                  <path v-if="!showPwd" d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" stroke="currentColor" stroke-width="2"/>
                  <circle v-if="!showPwd" cx="12" cy="12" r="3" stroke="currentColor" stroke-width="2"/>
                  <path v-if="showPwd" d="M17.94 17.94A10.07 10.07 0 0112 20c-7 0-11-8-11-8a18.45 18.45 0 015.06-5.94M9.9 4.24A9.12 9.12 0 0112 4c7 0 11 8 11 8a18.5 18.5 0 01-2.16 3.19m-6.72-1.07a3 3 0 11-4.24-4.24M1 1l22 22" stroke="currentColor" stroke-width="2" stroke-linecap="round"/>
                </svg>
              </button>
            </div>
          </div>

          <!-- Erreur -->
          <transition name="shake">
            <div v-if="error" class="flex items-start gap-2 p-3 rounded-xl text-sm"
                 style="background:#FEF2F2;color:#DC2626;border:1px solid #FECACA">
              <svg class="flex-shrink-0 mt-0.5" width="15" height="15" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="2"/><path d="M12 8v4m0 4h.01" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg>
              {{ error }}
            </div>
          </transition>

          <button type="submit" :disabled="loading"
            class="w-full flex items-center justify-center gap-2 rounded-xl font-bold transition-all"
            style="background:#FFCC00;color:#1C1B18;height:50px;font-family:Montserrat,sans-serif;font-size:15px"
            :style="loading ? 'opacity:.7' : ''"
            onmouseover="this.style.transform='translateY(-1px)';this.style.boxShadow='0 8px 20px rgba(255,204,0,.35)'"
            onmouseout="this.style.transform='';this.style.boxShadow=''">
            <svg v-if="loading" class="animate-spin" width="17" height="17" viewBox="0 0 24 24" fill="none">
              <circle cx="12" cy="12" r="10" stroke="rgba(0,0,0,.2)" stroke-width="3"/>
              <path d="M12 2a10 10 0 0110 10" stroke="#1C1B18" stroke-width="3" stroke-linecap="round"/>
            </svg>
            {{ loading ? 'Connexion…' : 'Se connecter' }}
          </button>
        </form>

        <div class="mt-7 pt-5" style="border-top:1px solid #F0EEE7">
          <div class="flex items-center justify-center gap-2 text-xs" style="color:#9C998F">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none"><rect x="4" y="11" width="16" height="10" rx="2" stroke="#21A05A" stroke-width="2"/><path d="M8 11V7a4 4 0 018 0v4" stroke="#21A05A" stroke-width="2" stroke-linecap="round"/></svg>
            Connexion sécurisée · plateforme interne MTN
          </div>
          <p class="text-xs mt-2 text-center" style="color:#B8B5AC">
            Pas de compte ? Contactez votre administrateur.
          </p>
        </div>
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

const features = ['VOC EBU', 'FTTH', '4G', 'Roaming', 'Jointure auto', 'Analyse NPS']

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

<style scoped>
.fade-up { animation: fadeUp .5s cubic-bezier(.21,1.02,.73,1) both; }
@keyframes fadeUp { from { opacity:0; transform:translateY(14px); } to { opacity:1; transform:translateY(0); } }
.shake-enter-active { animation: shake .4s; }
@keyframes shake { 0%,100%{transform:translateX(0)} 25%{transform:translateX(-4px)} 75%{transform:translateX(4px)} }
</style>
