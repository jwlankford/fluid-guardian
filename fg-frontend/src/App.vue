<script setup>
import { ref, onMounted, onUnmounted } from "vue";
import Dashboard from "./pages/Dashboard.vue";
import Reports from "./pages/Reports.vue";
import EnterFluid from "./pages/EnterFluid.vue";
import { useAuth } from "./composables/useAuth.js";

const { isLoggedIn, userProfile, login, logout } = useAuth();

const currentPage = ref("enter");
const isUserMenuOpen = ref(false);
const userMenuContainer = ref(null);

const navigateTo = (page) => {
  currentPage.value = page;
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
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>

<template>
  <div class="app-shell">
    <header class="app-header">
      <a class="brand" href="#" @click.prevent="navigateTo('enter')">
        Fluid Guardian
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
                @click="handleLogout"
                class="dropdown-action-btn"
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
      <EnterFluid v-else-if="currentPage === 'enter'" />
      <Reports v-else />
    </main>

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
          :class="{ active: currentPage === 'reports' }"
          @click="navigateTo('reports')"
        >
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
          <span>Reports</span>
        </button>
      </nav>
    </footer>


  </div>
</template>

<style>
:root {
  font-family: Arial, sans-serif;
  color: #1f2937;
  background: #e0f2fe; /* Light blue background */
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
  background: #e0f2fe;
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
  padding: 16px;
  padding-bottom: 80px; /* Space for the bottom nav */
}

.app-footer {
  position: sticky;
  bottom: 0;
  background-color: #ffffff;
  border-top: 1px solid #e5e7eb;
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
  color: #64748b;
  font-size: 0.75rem;
  gap: 4px;
}

.bottom-nav button.active {
  color: #0369a1;
  font-weight: bold;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 0;
  background-color: #0369a1; /* Blue header */
  padding: 16px 24px;
  color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.brand {
  color: inherit;
  font-size: 1.5rem;
  font-weight: 700;
  text-decoration: none;
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
  color: #334155;
  font-size: 0.75rem;
  font-weight: 600;
  cursor: pointer;
  box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
  transition: all 0.2s;
}

.login-btn:hover {
  background-color: #e2e8f0;
  border-color: rgba(59, 130, 246, 0.5);
  color: #0f172a;
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
  border: 1px solid #cbd5e1;
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
  width: 28px;
  height: 28px;
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
  color: #0f172a;
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
  color: #0f172a;
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
  color: #e11d48;
  background: transparent;
  border: none;
  font-size: 0.75rem;
  font-weight: 500;
  transition: background-color 0.2s;
  cursor: pointer;
}

.dropdown-action-btn:hover {
  background-color: #fff1f2;
}







</style>
