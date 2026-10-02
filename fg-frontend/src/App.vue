<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import Dashboard from "./pages/Dashboard.vue";
import Reports from "./pages/Reports.vue";
import EnterFluid from "./pages/EnterFluid.vue";
import Preferences from "./pages/Preferences.vue";
import Auth from "./pages/Auth.vue";
import HealthModal from "./components/HealthModal.vue";
import { useAuth } from "./composables/useAuth.js";
import logoLight from "./assets/images/logo-light.png";
import logoDark from "./assets/images/logo-dark.png";

const { isLoggedIn, userProfile, login, logout } = useAuth();

const currentPage = ref("dashboard");
const isUserMenuOpen = ref(false);
const isHealthModalOpen = ref(false);
const userMenuContainer = ref(null);

const isDarkMode = ref(localStorage.getItem('theme') === 'dark');
const resetMode = ref(localStorage.getItem('resetMode') || 'daily');
const measurementSystem = ref(localStorage.getItem('measurementSystem') || 'oz');
const fluidLimit = ref(Number(localStorage.getItem('fluidLimit')) || 64);
const refreshDashboardTrigger = ref(0);

import { provide } from 'vue';
provide('isDarkMode', isDarkMode);
provide('resetMode', resetMode);
provide('measurementSystem', measurementSystem);
provide('fluidLimit', fluidLimit);
provide('refreshDashboardTrigger', refreshDashboardTrigger);

const applyTheme = () => {
  if (isDarkMode.value) {
    document.documentElement.classList.add('dark');
  } else {
    document.documentElement.classList.remove('dark');
  }
};

const toggleTheme = () => {
  isDarkMode.value = !isDarkMode.value;
  localStorage.setItem('theme', isDarkMode.value ? 'dark' : 'light');
  applyTheme();
};
provide('toggleTheme', toggleTheme);

const navigateTo = (page) => {
  currentPage.value = page;
};

const globalAlert = ref({ show: false, message: "", type: "success", onConfirm: null });
provide('showAlert', (msg, type = "success", onConfirm = null) => { 
  globalAlert.value = { show: true, message: msg, type, onConfirm }; 
});

const handleIntakeLogged = (msg) => {
  globalAlert.value = { show: true, message: msg, type: "success", onConfirm: null };
  navigateTo('dashboard');
};

const handleLogin = () => {
  login();
};

const handleLogout = () => {
  logout();
  isUserMenuOpen.value = false;
};

const handleClickOutside = (event) => {
  if (userMenuContainer.value && !userMenuContainer.value.contains(event.target)) {
    isUserMenuOpen.value = false;
  }
};

onMounted(() => {
  applyTheme();
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <div id="app">
    <Auth v-if="!isLoggedIn" />
    <div v-else class="app-shell">
    <header class="app-header">
      <a class="brand" href="#" @click.prevent="navigateTo('enter')">
        <img :src="isDarkMode ? logoDark : logoLight" alt="Fluid Guardian" class="header-logo" />
      </a>
      
      <div class="auth-container" ref="userMenuContainer">
        <div class="user-menu-wrapper">
          <!-- Default Avatar (Not Logged In) -->
          <button
            v-if="!isLoggedIn"
            @click="handleLogin"
            class="avatar-btn"
            title="Sign In with Google"
          >
            <img
              src="https://ui-avatars.com/api/?name=Guest&background=e2e8f0&color=475569&rounded=true"
              alt="Guest Avatar"
              class="user-avatar"
            />
          </button>

          <!-- Logged In Avatar -->
          <button
            v-else
            @click="isUserMenuOpen = !isUserMenuOpen"
            class="avatar-btn"
            :class="{ 'menu-open': isUserMenuOpen }"
            title="User Menu & Profile Options"
          >
            <img
              :src="userProfile?.picture || 'https://ui-avatars.com/api/?name=User&background=bae6fd&color=0369a1&rounded=true'"
              :alt="userProfile?.name || 'User Avatar'"
              class="user-avatar"
            />
          </button>

          <!-- Dropdown Menu (Only shown when logged in and open) -->
          <div 
            v-if="isLoggedIn && isUserMenuOpen"
            class="dropdown-menu"
          >
            <!-- User Header Info -->
            <div class="dropdown-header">
              <img
                :src="userProfile?.picture || 'https://ui-avatars.com/api/?name=User&background=bae6fd&color=0369a1&rounded=true'"
                alt="User Avatar"
                class="dropdown-avatar"
              />
              <div class="dropdown-user-info">
                <div class="dropdown-name">{{ userProfile?.name || 'User' }}</div>
                <div class="dropdown-email">{{ userProfile?.email || 'user@example.com' }}</div>
              </div>
            </div>

            <!-- Menu Options -->
            <div class="dropdown-actions">
              <button 
                  @click="() => { navigateTo('preferences'); isUserMenuOpen = false; }"
                  class="dropdown-action-btn"
                >
                  <svg class="icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                  <span>Preferences</span>
                </button>
              <button 
                @click="handleLogout"
                class="dropdown-action-btn logout-btn"
              >
                <svg class="icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"/>
                </svg>
                <span>Log Out</span>
              </button>
            </div>
          </div>
        </div>
      </div>
    </header>

    <main class="app-main">
      <Dashboard v-if="currentPage === 'dashboard'" />
      <EnterFluid v-else-if="currentPage === 'enter'" @logged="handleIntakeLogged" />
      <Preferences v-else-if="currentPage === 'preferences'" />
      <Reports v-else />
    </main>

    <div v-if="globalAlert.show" class="alert-overlay" @click.self="globalAlert.show = false">
      <div class="alert-modal">
        <div class="alert-icon" :class="globalAlert.type">
          <svg v-if="globalAlert.type === 'success'" width="40" height="40" fill="none" stroke="#22c55e" stroke-width="3" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7" />
          </svg>
          <svg v-else-if="globalAlert.type === 'error'" width="40" height="40" fill="none" stroke="#ef4444" stroke-width="3" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <svg v-else width="40" height="40" fill="none" stroke="#f59e0b" stroke-width="3" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </div>
        <h3>
          <template v-if="globalAlert.type === 'success'">Success!</template>
          <template v-else-if="globalAlert.type === 'error'">Oops!</template>
          <template v-else>Are you sure?</template>
        </h3>
        <p>{{ globalAlert.message }}</p>
        
        <div v-if="globalAlert.type === 'confirm'" class="alert-actions">
          <button class="alert-btn cancel-btn" @click="globalAlert.show = false">Cancel</button>
          <button class="alert-btn confirm-btn" @click="() => { globalAlert.show = false; if(globalAlert.onConfirm) globalAlert.onConfirm(); }">Yes, reset</button>
        </div>
        <button v-else class="alert-btn" :class="globalAlert.type" @click="globalAlert.show = false">
          {{ globalAlert.type === 'success' ? 'Awesome' : 'Okay' }}
        </button>
      </div>
    </div>

    <footer class="app-footer">
      <nav class="bottom-nav">
        <button
          :class="{ active: currentPage === 'dashboard' }"
          @click="navigateTo('dashboard')"
        >
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
          <span>Dashboard</span>
        </button>
        <button
          :class="{ active: currentPage === 'enter' }"
          @click="navigateTo('enter')"
        >
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" /></svg>
          <span>Log</span>
        </button>
        <button
          @click="isHealthModalOpen = true"
        >
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
          <span>Health</span>
        </button>
        <button
          :class="{ active: currentPage === 'reports' }"
          @click="navigateTo('reports')"
        >
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
          <span>Reports</span>
        </button>
      </nav>
    </footer>

    <HealthModal :is-open="isHealthModalOpen" @close="isHealthModalOpen = false" />

    </div>
  </div>
</template>

<style>

h1, h2, h3, h4, h5, h6, .brand, .page-title, .section-title {
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
}

:root {
  font-family: 'Open Sans', Arial, sans-serif;
  color: #0A0A0A;
  background: #F8F9FA; /* Light blue background */
  font-synthesis: none;
  text-rendering: optimizeLegibility;
  box-sizing: border-box;
}

*, *::before, *::after {
  box-sizing: inherit;
}

body {
  min-width: 320px;
  margin: 0;
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 100vh;
  background-color: #1a1a1a;
}

#app {
  width: 375px;
  height: 667px;
  background: #F8F9FA;
  overflow-x: hidden;
  overflow-y: auto;
  box-shadow: 0 0 20px rgba(0,0,0,0.5);
  position: relative;
}

button {
  font: inherit;
  cursor: pointer;
}

.app-shell {
  width: 100%;
  min-height: 100%;
  margin: 0;
  padding: 0;
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
}

.app-main {
  flex: 1;
  padding: 10px;
  padding-bottom: 80px; /* Space for the bottom nav */
}

.app-footer {
  position: sticky;
  bottom: 0;
  background-color: #007BFF;
  border-top: none;
  z-index: 50;
  box-shadow: 0 -4px 6px -1px rgba(0, 0, 0, 0.05);
}

.bottom-nav {
  display: flex;
  justify-content: space-around;
  padding: 8px 0;
}

.bottom-nav button {
  display: flex;
  flex-direction: column;
  align-items: center;
  background: transparent;
  border: none;
  color: rgba(255,255,255,0.7);
  font-size: 0.75rem;
  gap: 4px;
}

.bottom-nav button.active {
  color: #FFFFFF;
  font-weight: bold;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 0;
  background-color: #007BFF;
  padding: 10px;
  color: #FFFFFF;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.brand {
  color: inherit;
  display: flex;
  align-items: center;
  text-decoration: none;
}

.header-logo {
  height: 48px;
  width: auto;
  object-fit: contain;
  filter: drop-shadow(0 2px 4px rgba(0,0,0,0.2));
}

.auth-container {
  display: flex;
  align-items: center;
  position: relative;
}

.user-menu-wrapper {
  position: relative;
}

.login-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background-color: #f1f5f9;
  color: #333333;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.login-btn:hover {
  background-color: #e2e8f0;
  border-color: rgba(59, 130, 246, 0.5);
  color: #0A0A0A;
}

.icon-svg {
  width: 14px;
  height: 14px;
  color: #2563eb;
}

.avatar-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2px;
  border-radius: 9999px;
  background-color: #f1f5f9;
  border: 1px solid #C0C0C0;
  transition: all 0.2s;
  cursor: pointer;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
}

.avatar-btn:hover {
  border-color: rgba(59, 130, 246, 0.5);
  background-color: #e2e8f0;
  transform: scale(1.05);
}

.avatar-btn.menu-open {
  border-color: #3b82f6;
  box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.3);
  background-color: #eff6ff;
}

.user-avatar {
  width: 35px;
  height: 35px;
  border-radius: 9999px;
  object-fit: cover;
  box-shadow: 0 0 0 1.5px rgba(96, 165, 250, 0.5);
}

.dropdown-menu {
  position: absolute;
  right: 0;
  top: 100%;
  margin-top: 8px;
  width: 256px;
  background-color: #ffffff;
  border: 1px solid #e2e8f0;
  border-radius: 16px;
  box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.25);
  padding-top: 8px;
  padding-bottom: 8px;
  z-index: 50;
  color: #0A0A0A;
}

.dropdown-header {
  padding: 10px 16px;
  border-bottom: 1px solid #f1f5f9;
  display: flex;
  align-items: center;
  gap: 10px;
}

.dropdown-avatar {
  width: 32px;
  height: 32px;
  border-radius: 9999px;
  object-fit: cover;
  box-shadow: 0 0 0 1px rgba(96, 165, 250, 0.4);
}

.dropdown-user-info {
  overflow: hidden;
}

.dropdown-name {
  font-size: 0.75rem;
  font-weight: 700;
  color: #0A0A0A;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-email {
  font-size: 0.625rem;
  font-family: monospace;
  color: #2563eb;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dropdown-actions {
  border-top: 1px solid #f1f5f9;
  padding-top: 6px;
  margin-top: 6px;
}

.dropdown-action-btn {
  width: 100%;
  padding: 8px 16px;
  text-align: left;
  display: flex;
  align-items: center;
  gap: 10px;
  background: transparent;
  border: none;
  font-size: 0.75rem;
  font-weight: 500;
  transition: background-color 0.2s;
  cursor: pointer;
  color: #333333;
}
.dropdown-action-btn:hover {
  background-color: #f1f5f9;
}
.logout-btn {
  color: #e11d48;
}
.logout-btn:hover {
  background-color: #fff1f2;
}

.alert-overlay {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 100;
  animation: fadeIn 0.2s;
}

.alert-modal {
  background: #FFFFFF;
  padding: 32px;
  border-radius: 20px;
  text-align: center;
  width: 90%;
  max-width: 320px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  animation: scaleUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.alert-icon {
  background: #dcfce7;
  width: 64px;
  height: 64px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto 16px;
}

.alert-modal h3 {
  margin: 0 0 8px;
  color: #0A0A0A !important;
  font-size: 1.75rem;
  font-family: 'Montserrat', sans-serif;
  font-weight: 700;
}

.alert-modal p {
  color: #666666 !important;
  margin: 0 0 24px;
  font-size: 1rem;
}

.alert-btn {
  background: #22c55e;
  color: white;
  border: none;
  border-radius: 12px;
  padding: 12px 24px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  width: 100%;
  transition: background 0.2s;
}

.alert-btn:hover {
  background: #16a34a;
}

.alert-actions {
  display: flex;
  gap: 12px;
}

.alert-btn.cancel-btn {
  background: transparent;
  color: #C0C0C0;
  border: 1px solid #C0C0C0;
}
.alert-btn.cancel-btn:hover {
  background: rgba(192,192,192,0.1);
}

.alert-btn.confirm-btn {
  background: #ef4444;
}
.alert-btn.confirm-btn:hover {
  background: #dc2626;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes scaleUp {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

/* Dark Mode Overrides */
html.dark body { background-color: #0A0A0A; }
html.dark #app { background: #0A0A0A; color: #f8fafc; }
html.dark .app-header, html.dark .app-footer { background-color: #0b1e47; }

html.dark .dropdown-menu { background-color: #141414; border-color: #333333; color: #f8fafc; }
html.dark .dropdown-header { border-bottom-color: #333333; }
html.dark .dropdown-actions { border-top-color: #333333; }
html.dark .dropdown-name { color: #f8fafc; }
html.dark .dropdown-action-btn { color: #C0C0C0; }
html.dark .dropdown-action-btn:hover { background-color: #333333; }
html.dark .logout-btn { color: #fda4af; }
html.dark .logout-btn:hover { background-color: rgba(225, 29, 72, 0.2); }

html.dark .alert-modal {
  background: #141414;
  box-shadow: 0 10px 25px rgba(0,0,0,0.5);
}

html.dark .alert-modal h3 {
  color: #FFFFFF !important;
}

html.dark .alert-modal p {
  color: #C0C0C0 !important;
}

/* Global dark overrides for other components */
html.dark .card, html.dark .auth-card, html.dark .report, html.dark .enter-page, html.dark .submit-section { background-color: #141414; color: #f8fafc; box-shadow: 0 4px 6px rgba(0,0,0,0.3); border-color: #333333; }
html.dark .submit-section { box-shadow: none; }
html.dark .page-title, html.dark h1, html.dark h2, html.dark h3 { color: #F8F9FA !important; }
html.dark .section-title, html.dark label, html.dark p { color: #C0C0C0; }
html.dark .bottom-nav button { color: rgba(255,255,255,0.7); }
html.dark .bottom-nav button.active { color: #FFFFFF; }
html.dark .input-group input, html.dark .custom-input-group input { background: #333333; border-color: #444444; color: #f8fafc; }
html.dark .symptom-btn { background: #333333; border-color: #444444; color: #f8fafc; }
html.dark .symptom-btn.active { background: #0c4a6e; border-color: #007BFF; color: #F8F9FA; }
html.dark .modal-content { background: #141414; color: #f8fafc; }
html.dark .alert-modal { background: #141414; color: #f8fafc; }
html.dark .alert-modal p { color: #C0C0C0; }
html.dark .oz-display { fill: #F8F9FA; text-shadow: 0 0 8px rgba(0,0,0,0.8); }
html.dark .scan-btn, html.dark .small-cup-btn svg { border-color: #444444; color: #C0C0C0; stroke: #00CFFF; }
html.dark .scan-btn { background: #333333; }
html.dark .empty-text { color: #666666; }
html.dark .risk-bar-wrapper { background: #333333; }
html.dark .risk-mask { background: #333333; }
html.dark .slider-track { stroke: #333333 !important; }
html.dark .limit { color: #C0C0C0; }
html.dark .consumed { color: #F8F9FA; }
html.dark .consumed.danger-text, html.dark .danger-text { color: #fca5a5; }
html.dark .over-limit-warning { color: #fca5a5; }
html.dark .reset-btn { border-color: #f87171; color: #f87171; }
html.dark .reset-btn:hover { background-color: rgba(248, 113, 113, 0.1); }
html.dark .symptom-item::before { color: #f87171; }







</style>
