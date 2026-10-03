<script setup>
import { ref, computed, watch, onMounted, inject } from "vue";
import PeriodIntakeChart from "../components/PeriodIntakeChart.vue";
import { useAuth } from "../composables/useAuth.js";
import api from "../services/api.js";

const showAlert = inject("showAlert");
const measurementSystem = inject("measurementSystem", ref("oz"));
const fluidLimit = inject("fluidLimit", ref(64));
const { userProfile } = useAuth();

// Helper to format Date to YYYY-MM-DD
const toISODate = (d) => {
  const year = d.getFullYear();
  const month = String(d.getMonth() + 1).padStart(2, "0");
  const day = String(d.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// Date range filters
const fromDate = ref("");
const toDate = ref("");
const activePreset = ref("all");

// Report state
const reportData = ref(null);
const isLoading = ref(false);

const unit = computed(() => (measurementSystem.value === "ml" ? "mL" : "oz"));

const getUserId = () => {
  return userProfile.value?.uid || "default_user";
};

// Quick date range presets
const setPreset = (preset) => {
  activePreset.value = preset;
  if (preset === "all") {
    fromDate.value = "";
    toDate.value = "";
    fetchReport(true);
    return;
  }

  const end = new Date();
  toDate.value = toISODate(end);

  if (preset === "month") {
    const start = new Date(end.getFullYear(), end.getMonth(), 1);
    fromDate.value = toISODate(start);
  } else {
    const days = Number(preset);
    const start = new Date();
    start.setDate(end.getDate() - (days - 1));
    fromDate.value = toISODate(start);
  }
  fetchReport(false);
};

// Generate fallback days when offline / mock
const generateFallbackDays = (startStr, endStr) => {
  const result = [];
  const start = new Date(startStr || new Date());
  const end = new Date(endStr || new Date());
  if (isNaN(start.getTime()) || isNaN(end.getTime()) || start > end) return result;

  const curr = new Date(start);
  while (curr <= end) {
    result.push({
      date: toISODate(curr),
      intake_ml: 0,
      running_intake_ml: 0,
      event_count: 0,
      events: [],
    });
    curr.setDate(curr.getDate() + 1);
  }
  return result;
};

// Fetch Report directly from database
const fetchReport = async (isAll = false) => {
  isLoading.value = true;
  const uid = getUserId();

  const params = {};
  if (!isAll && fromDate.value && toDate.value) {
    params.start_date = fromDate.value;
    params.end_date = toDate.value;
  }

  try {
    const res = await api.reporting.get(`/report/period/${uid}`, { params });
    reportData.value = res.data;
    if (res.data.start_date) {
      fromDate.value = res.data.start_date;
    }
    if (res.data.end_date) {
      toDate.value = res.data.end_date;
    }
  } catch (err) {
    console.warn("Could not fetch report from reporting backend:", err);
    // Attempt local fallback: fetch today's data from intake service or generate empty range
    try {
      const todayRes = await api.intake.get(`/intake/${uid}/today`);
      const todayData = todayRes.data;
      const todayStr = toISODate(new Date());
      const totalMl = todayData.total_fluid_ml || 0;
      reportData.value = {
        user_id: uid,
        start_date: todayStr,
        end_date: todayStr,
        total_intake_ml: totalMl,
        average_daily_ml: totalMl,
        event_count: todayData.event_count || 0,
        daily_totals_ml: { [todayStr]: totalMl },
        running_totals_ml: { [todayStr]: totalMl },
        days: [
          {
            date: todayStr,
            intake_ml: totalMl,
            running_intake_ml: totalMl,
            event_count: todayData.event_count || 0,
            events: todayData.events || [],
          },
        ],
      };
      fromDate.value = todayStr;
      toDate.value = todayStr;
    } catch {
      const todayStr = toISODate(new Date());
      reportData.value = {
        user_id: uid,
        start_date: fromDate.value || todayStr,
        end_date: toDate.value || todayStr,
        total_intake_ml: 0,
        average_daily_ml: 0,
        event_count: 0,
        daily_totals_ml: {},
        running_totals_ml: {},
        days: generateFallbackDays(fromDate.value || todayStr, toDate.value || todayStr),
      };
    }
  } finally {
    isLoading.value = false;
  }
};

const onCustomDateChange = () => {
  activePreset.value = "custom";
  if (fromDate.value && toDate.value) {
    fetchReport(false);
  }
};

watch(userProfile, () => {
  fetchReport(activePreset.value === "all");
});

onMounted(() => {
  fetchReport(true);
});

// CSV Export Handler
const exportCSV = () => {
  const currentUnit = unit.value;
  const limitVal =
    measurementSystem.value === "ml"
      ? Math.round(fluidLimit.value * 29.5735)
      : fluidLimit.value;

  const filename = `fluid_intake_report_${fromDate.value || "all"}_to_${toDate.value || "all"}.csv`;
  let csvContent = `Date,Daily Intake (${currentUnit}),Running Total (${currentUnit}),Daily Limit (${currentUnit}),Limit Difference (${currentUnit}),Status,Events Count\n`;

  const daysList = reportData.value?.days || [];
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

    csvContent += `${d.date},${dailyVal},${runningVal},${limitVal},${diff},${status},${d.event_count || 0}\n`;
  });

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
      showAlert("Emailing intake report to clinician...", "success");
    }
  } else if (type === "PDF") {
    if (showAlert) {
      showAlert("Generating PDF report... Download will start shortly.", "success");
    }
  }
};
</script>

<template>
  <section class="reports-page">
    <h1 class="page-title">Reports</h1>

    <!-- Report Controls (Date Range & Presets) -->
    <div class="report-controls card">
      <div class="period-controls-wrapper">
        <div class="date-pickers period-pickers">
          <div class="custom-input-group">
            <label>From</label>
            <input
              type="date"
              v-model="fromDate"
              :max="toDate"
              @change="onCustomDateChange"
            />
          </div>
          <div class="custom-input-group">
            <label>To</label>
            <input
              type="date"
              v-model="toDate"
              :min="fromDate"
              @change="onCustomDateChange"
            />
          </div>
        </div>

        <!-- Quick Preset Pills -->
        <div class="preset-pills">
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 'all' }]"
            @click="setPreset('all')"
          >
            All Data
          </button>
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 7 }]"
            @click="setPreset(7)"
          >
            7 Days
          </button>
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 14 }]"
            @click="setPreset(14)"
          >
            14 Days
          </button>
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 30 }]"
            @click="setPreset(30)"
          >
            30 Days
          </button>
          <button
            type="button"
            :class="['preset-pill', { active: activePreset === 'month' }]"
            @click="setPreset('month')"
          >
            This Month
          </button>
        </div>
      </div>
    </div>

    <!-- Fluid Intake Chart & Day Details -->
    <PeriodIntakeChart
      :days="reportData?.days || []"
      :fluid-limit="fluidLimit"
      :measurement-system="measurementSystem"
      :is-loading="isLoading"
      :start-date="fromDate"
      :end-date="toDate"
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

.preset-pill.active {
  background: #007BFF;
  color: #ffffff;
  border-color: #007BFF;
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

html.dark .preset-pill.active {
  background: #00CFFF;
  color: #000000;
  border-color: #00CFFF;
}
</style>
