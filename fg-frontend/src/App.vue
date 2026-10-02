<script setup>
import { ref } from "vue";
import Dashboard from "./pages/Dashboard.vue";
import Reports from "./pages/Reports.vue";

const currentPage = ref("dashboard");
</script>

<template>
  <main class="app-shell">
    <header class="app-header">
      <a class="brand" href="#" @click.prevent="currentPage = 'dashboard'">
        Fluid Guardian
      </a>
      <nav aria-label="Main navigation">
        <button
          :aria-current="currentPage === 'dashboard' ? 'page' : undefined"
          @click="currentPage = 'dashboard'"
        >
          Dashboard
        </button>
        <button
          :aria-current="currentPage === 'reports' ? 'page' : undefined"
          @click="currentPage = 'reports'"
        >
          Reports
        </button>
      </nav>
    </header>

    <Dashboard v-if="currentPage === 'dashboard'" />
    <Reports v-else />
  </main>
</template>

<style>
:root {
  font-family: Arial, sans-serif;
  color: #1f2937;
  background: #f3f6f8;
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

body {
  min-width: 320px;
  margin: 0;
}

button {
  font: inherit;
  cursor: pointer;
}

.app-shell {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px;
}

.app-header,
.app-header nav {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}

.app-header {
  margin-bottom: 32px;
}

.brand {
  color: inherit;
  font-size: 1.25rem;
  font-weight: 700;
  text-decoration: none;
}

.app-header button {
  padding: 8px 12px;
  border: 0;
  border-radius: 6px;
  background: transparent;
}

.app-header button[aria-current="page"] {
  background: #dceef3;
  color: #14566b;
}
</style>
