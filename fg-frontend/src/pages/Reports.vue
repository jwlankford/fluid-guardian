<script setup>
import { ref, inject } from "vue";
import DailyReport from "../components/DailyReport.vue";

const showAlert = inject('showAlert');
const reportType = ref('day');
const singleDate = ref('');
const fromDate = ref('');
const toDate = ref('');

const handleExport = (type) => {
  if (showAlert) {
    showAlert(`Exporting report as ${type}... (Coming soon!)`);
  } else {
    alert(`Exporting report as ${type}... (Coming soon!)`);
  }
};
</script>

<template>
  <section class="reports-page">
    <h1 class="page-title">Reports</h1>

    <!-- Report Controls (Toggle & Dates) -->
    <div class="report-controls card">
      <div class="toggle-group">
        <button 
          :class="['toggle-btn', { active: reportType === 'day' }]" 
          @click="reportType = 'day'"
        >By Day</button>
        <button 
          :class="['toggle-btn', { active: reportType === 'period' }]" 
          @click="reportType = 'period'"
        >By Period</button>
      </div>

      <div v-if="reportType === 'day'" class="date-pickers">
        <div class="custom-input-group">
          <label>Select Date</label>
          <input type="date" v-model="singleDate" />
        </div>
      </div>
      <div v-else class="date-pickers period-pickers">
        <div class="custom-input-group">
          <label>From</label>
          <input type="date" v-model="fromDate" />
        </div>
        <div class="custom-input-group">
          <label>To</label>
          <input type="date" v-model="toDate" />
        </div>
      </div>
    </div>
    
    <DailyReport />
    
    <div class="report-actions">
      <button class="action-btn" title="Email Report" @click="handleExport('Email')">
        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      </button>
      <button class="action-btn" title="Download PDF" @click="handleExport('PDF')">
        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
      </button>
      <button class="action-btn" title="Download CSV" @click="handleExport('CSV')">
        <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 10h18M7 15h1m4 0h1m-7 4h12a3 3 0 003-3V8a3 3 0 00-3-3H6a3 3 0 00-3 3v8a3 3 0 003 3z" />
        </svg>
      </button>
    </div>
  </section>
</template>

<style scoped>
.reports-page {
  padding: 1rem;
  padding-bottom: 5rem;
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  color: #007BFF;
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0 0 1.5rem 0;
}

.report-controls {
  padding: 16px;
  margin-bottom: 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #e2e8f0;
}

.toggle-group {
  display: flex;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 16px;
}

.toggle-btn {
  flex: 1;
  padding: 8px 16px;
  border: none;
  background: transparent;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 600;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn.active {
  background: white;
  color: #0f172a;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
}

.date-pickers {
  display: flex;
  gap: 16px;
}

.custom-input-group {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 6px;
}

.custom-input-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.custom-input-group input {
  padding: 10px 12px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.95rem;
  color: #333333;
  background: #ffffff;
  transition: border-color 0.2s;
}

.custom-input-group input:focus {
  outline: none;
  border-color: #007BFF;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

.report-actions {
  display: flex;
  justify-content: flex-end;
  gap: 16px;
  margin-top: 16px;
}

.action-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  background: white;
  border: 1px solid #e2e8f0;
  border-radius: 50%;
  color: #007BFF;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.action-btn:hover {
  background: #f8fafc;
  transform: translateY(-2px);
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  border-color: #007BFF;
}

/* Dark mode overrides */
html.dark .action-btn {
  background: #141414;
  border-color: #333333;
  color: #00CFFF;
}

html.dark .action-btn:hover {
  background: #222222;
  border-color: #00CFFF;
}

html.dark .report-controls {
  background: #141414;
  border-color: #333333;
}

html.dark .toggle-group {
  background: #222222;
}

html.dark .toggle-btn {
  color: #94a3b8;
}

html.dark .toggle-btn.active {
  background: #333333;
  color: #f8fafc;
}

html.dark .custom-input-group label {
  color: #94a3b8;
}

html.dark .custom-input-group input {
  background: #1e1e1e;
  border-color: #333333;
  color: #f8fafc;
}

html.dark .custom-input-group input:focus {
  border-color: #00CFFF;
  box-shadow: 0 0 0 2px rgba(0, 207, 255, 0.2);
}
</style>
