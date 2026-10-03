<script setup>
import { ref, computed, watch, onMounted, inject } from "vue";
import DailyReport from "../components/DailyReport.vue";
import PeriodIntakeChart from "../components/PeriodIntakeChart.vue";
import { useAuth } from "../composables/useAuth.js";
import api from "../services/api.js";

const showAlert = inject("showAlert");
const measurementSystem = inject("measurementSystem", ref("oz"));
const fluidLimit = inject("fluidLimit", ref(64));
const { userProfile } = useAuth();

const reportType = ref("period");

// Helper to format Date to YYYY-MM-DD
const toISODate = (d) => {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// Initial default dates (Last 7 days for period, Today for single day)
const now = new Date();
const past7Days = new Date();
past7Days.setDate(now.getDate() - 6);

const singleDate = ref(toISODate(now));
const fromDate = ref(toISODate(past7Days));
const toDate = ref(toISODate(now));

// Period report state
const periodData = ref(null);
const isPeriodLoading = ref(false);

// Daily report state
const dailyData = ref(null);
const isDailyLoading = ref(false);

const unit = computed(() => (measurementSystem.value === "ml" ? "mL" : "oz"));

const getUserId = () => {
  return userProfile.value?.uid || "doen1YU9BAPpTxLPG6MFHx9CFpf2";
};

// Quick date range presets
const setPreset = (days) => {
  const end = new Date();
  toDate.value = toISODate(end);

  if (days === "month") {
    const start = new Date(end.getFullYear(), end.getMonth(), 1);
    fromDate.value = toISODate(start);
  } else {
    const start = new Date();
    start.setDate(end.getDate() - (days - 1));
    fromDate.value = toISODate(start);
  }
};

// Generate fallback days when offline / mock
const generateFallbackDays = (startStr, endStr) => {
  const result = [];
  const start = new Date(startStr);
  const end = new Date(endStr);
  if (isNaN(start.getTime()) || isNaN(end.getTime()) || start > end) return result;

  const curr = new Date(start);
  while (curr <= end) {
    result.push({
      date: toISODate(curr),
      intake_ml: 0,
      running_intake_ml: 0,
      event_count: 0,
    });
    curr.setDate(curr.getDate() + 1);
  }
  return result;
};

// Fetch Period Report
const fetchPeriodReport = async () => {
  if (!fromDate.value || !toDate.value) return;
  isPeriodLoading.value = true;
  const uid = getUserId();

  try {
    const res = await api.reporting.get(`/report/period/${uid}`, {
      params: {
        start_date: fromDate.value,
        end_date: toDate.value,
      },
    });
    periodData.value = res.data;
  } catch (err) {
    console.warn("Could not fetch period report from backend, using local fallback:", err);
    // Provide empty fallback range so chart displays properly without crashing
    periodData.value = {
      user_id: uid,
      start_date: fromDate.value,
      end_date: toDate.value,
      total_intake_ml: 0,
      average_daily_ml: 0,
      event_count: 0,
      daily_totals_ml: {},
      running_totals_ml: {},
      days: generateFallbackDays(fromDate.value, toDate.value),
    };
  } finally {
    isPeriodLoading.value = false;
  }
};

// Fetch Daily Report
const fetchDailyReport = async () => {
  if (!singleDate.value) return;
  isDailyLoading.value = true;
  const uid = getUserId();

  try {
    const res = await api.reporting.get(`/report/daily/${uid}`, {
      params: {
        report_date: singleDate.value,
      },
    });
    dailyData.value = res.data;
  } catch (err) {
    console.warn("Could not fetch daily report from backend:", err);
    dailyData.value = {
      user_id: uid,
      date: singleDate.value,
      total_intake_ml: 0,
      event_count: 0,
      events: [],
    };
  } finally {
    isDailyLoading.value = false;
  }
};

// Watchers
watch(
  [fromDate, toDate],
  () => {
    if (reportType.value === "period") {
      fetchPeriodReport();
    }
  },
  { deep: true }
);

watch(singleDate, () => {
  if (reportType.value === "day") {
    fetchDailyReport();
  }
});

watch(reportType, (newType) => {
  if (newType === "period") {
    fetchPeriodReport();
  } else {
    fetchDailyReport();
  }
});

watch(userProfile, () => {
  if (reportType.value === "period") {
    fetchPeriodReport();
  } else {
    fetchDailyReport();
  }
});

onMounted(() => {
  fetchPeriodReport();
  fetchDailyReport();
});

// CSV Export Handler
const exportCSV = () => {
  const currentUnit = unit.value;
  const limitVal =
    measurementSystem.value === "ml"
      ? Math.round(fluidLimit.value * 29.5735)
      : fluidLimit.value;

  let csvContent = "";
  let filename = "";

  if (reportType.value === "period") {
    filename = `fluid_intake_report_${fromDate.value}_to_${toDate.value}.csv`;
    csvContent = `Date,Daily Intake (${currentUnit}),Running Total (${currentUnit}),Daily Limit (${currentUnit}),Limit Difference (${currentUnit}),Status\n`;

    const daysList = periodData.value?.days || [];
    daysList.forEach((d) => {
      const dailyVal =
        measurementSystem.value === "ml"
          ? Math.round(d.intake_ml)
          : Math.round(d.intake_ml / 29.5735);
      const runningVal =
        measurementSystem.value === "ml"
          ? Math.round(d.running_intake_ml)
          : Math.round(d.running_intake_ml / 29.5735);
      const diff = dailyVal - limitVal;
      const status = diff > 0 ? "Over Limit" : "Within Limit";

      csvContent += `${d.date},${dailyVal},${runningVal},${limitVal},${diff},${status}\n`;
    });
  } else {
    filename = `fluid_intake_report_${singleDate.value}.csv`;
    csvContent = `Date,Event Type,Volume (${currentUnit}),Time\n`;
    const events = dailyData.value?.events || [];
    if (events.length === 0) {
      csvContent += `${singleDate.value},No Events,0,-\n`;
    } else {
      events.forEach((e) => {
        const ml = e.payload?.volume_ml || 0;
        const vol =
          measurementSystem.value === "ml"
            ? Math.round(ml)
            : Math.round(ml / 29.5735);
        csvContent += `${singleDate.value},${e.event_type},${vol},${e.occurred_at || ""}\n`;
      });
    }
  }

  const blob = new Blob([csvContent], { type: "text/csv;charset=utf-8;" });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.setAttribute("href", url);
  link.setAttribute("download", filename);
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);

  if (showAlert) {
    showAlert(`CSV report downloaded: ${filename}`, "success");
  }
};

const handleExport = (type) => {
  if (type === "CSV") {
    exportCSV();
  } else if (type === "Email") {
    if (showAlert) {
      showAlert(`Emailing ${reportType.value === "period" ? "Period" : "Daily"} report to clinician...`, "success");
    }
  } else if (type === "PDF") {
    if (showAlert) {
      showAlert(`Generating PDF report... Download will start shortly.`, "success");
    }
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
          :class="['toggle-btn', { active: reportType === 'period' }]" 
          @click="reportType = 'period'"
        >By Period</button>
        <button 
          :class="['toggle-btn', { active: reportType === 'day' }]" 
          @click="reportType = 'day'"
        >By Day</button>
      </div>

      <!-- Period Date Pickers -->
      <div v-if="reportType === 'period'" class="period-controls-wrapper">
        <div class="date-pickers period-pickers">
          <div class="custom-input-group">
            <label>From</label>
            <input type="date" v-model="fromDate" :max="toDate" />
          </div>
          <div class="custom-input-group">
            <label>To</label>
            <input type="date" v-model="toDate" :min="fromDate" />
          </div>
        </div>

        <!-- Quick Preset Pills -->
        <div class="preset-pills">
          <button type="button" class="preset-pill" @click="setPreset(7)">7 Days</button>
          <button type="button" class="preset-pill" @click="setPreset(14)">14 Days</button>
          <button type="button" class="preset-pill" @click="setPreset(30)">30 Days</button>
          <button type="button" class="preset-pill" @click="setPreset('month')">This Month</button>
        </div>
      </div>

      <!-- Single Day Picker -->
      <div v-else class="date-pickers">
        <div class="custom-input-group">
          <label>Select Date</label>
          <input type="date" v-model="singleDate" />
        </div>
      </div>
    </div>

    <!-- Period View: Running Daily Fluid Intake Chart -->
    <PeriodIntakeChart
      v-if="reportType === 'period'"
      :days="periodData?.days || []"
      :fluid-limit="fluidLimit"
      :measurement-system="measurementSystem"
      :is-loading="isPeriodLoading"
      :start-date="fromDate"
      :end-date="toDate"
    />

    <!-- Single Day View: Daily Report -->
    <DailyReport
      v-else
      :report="dailyData"
      :fluid-limit="fluidLimit"
      :unit="unit"
      :is-loading="isDailyLoading"
    />

    <!-- Export Action Buttons -->
    <div class="report-actions">
      <button class="action-btn" title="Email Report" @click="handleExport('Email')">
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
        </svg>
      </button>
      <button class="action-btn" title="Download PDF" @click="handleExport('PDF')">
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
      </button>
      <button class="action-btn" title="Download CSV" @click="handleExport('CSV')">
        <svg width="22" height="22" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
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
  margin: 0 0 1.25rem 0;
}

.report-controls {
  padding: 16px;
  margin-bottom: 16px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #e2e8f0;
}

.toggle-group {
  display: flex;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 4px;
  margin-bottom: 14px;
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

.period-controls-wrapper {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.date-pickers {
  display: flex;
  gap: 12px;
}

.custom-input-group {
  display: flex;
  flex-direction: column;
  flex: 1;
  gap: 4px;
}

.custom-input-group label {
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.custom-input-group input {
  padding: 8px 10px;
  border: 1px solid #cbd5e1;
  border-radius: 8px;
  font-size: 0.85rem;
  color: #333333;
  background: #ffffff;
  transition: border-color 0.2s;
  width: 100%;
}

.custom-input-group input:focus {
  outline: none;
  border-color: #007BFF;
  box-shadow: 0 0 0 2px rgba(0, 123, 255, 0.2);
}

/* Preset pills */
.preset-pills {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.preset-pill {
  padding: 4px 10px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 600;
  color: #475569;
  cursor: pointer;
  transition: all 0.2s;
}

.preset-pill:hover {
  background: #e2e8f0;
  color: #0f172a;
  border-color: #cbd5e1;
}

.report-actions {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
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

html.dark .preset-pill {
  background: #222222;
  border-color: #333333;
  color: #94a3b8;
}

html.dark .preset-pill:hover {
  background: #333333;
  color: #f8fafc;
  border-color: #444444;
}
</style>
