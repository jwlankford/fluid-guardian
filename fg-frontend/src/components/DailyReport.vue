<script setup>
import { computed } from "vue";

const props = defineProps({
  summary: {
    type: String,
    default: "",
  },
  report: {
    type: Object,
    default: null,
  },
  unit: {
    type: String,
    default: "oz",
  },
  fluidLimit: {
    type: Number,
    default: 64,
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
});

const displayConsumed = computed(() => {
  if (!props.report) return 0;
  return (props.unit || "").toLowerCase() === "ml"
    ? Math.round(props.report.total_intake_ml || 0)
    : Math.round((props.report.total_intake_ml || 0) / 29.5735);
});

const displayLimit = computed(() => {
  return (props.unit || "").toLowerCase() === "ml"
    ? Math.round(props.fluidLimit * 29.5735)
    : props.fluidLimit;
});

const isOverLimit = computed(() => {
  return displayConsumed.value > displayLimit.value;
});

const formattedDate = computed(() => {
  if (!props.report?.date) return "Selected Date";
  const [y, m, d] = String(props.report.date).split("-");
  if (!y || !m || !d) return props.report.date;
  const dateObj = new Date(parseInt(y), parseInt(m) - 1, parseInt(d));
  return dateObj.toLocaleDateString("en-US", {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: "numeric",
  });
});

const formatEventTime = (isoString) => {
  if (!isoString) return "";
  const d = new Date(isoString);
  return d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
};

const getEventVolume = (event) => {
  const ml = event.payload?.volume_ml;
  if (ml === undefined || ml === null) return null;
  return (props.unit || "").toLowerCase() === "ml"
    ? `${Math.round(ml)} mL`
    : `${Math.round(ml / 29.5735)} oz`;
};
</script>

<template>
  <section class="daily-report-card card">
    <div class="report-header">
      <div class="header-icon">
        <svg width="22" height="22" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
      <div>
        <h2 class="report-title">Daily Summary</h2>
        <span class="report-subtitle">{{ formattedDate }}</span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="loading-state">
      <div class="spinner"></div>
      <p>Loading daily data...</p>
    </div>

    <div v-else class="report-content">
      <!-- Intake overview banner -->
      <div class="intake-summary-box" :class="{ 'warning-box': isOverLimit }">
        <div class="summary-numbers">
          <span class="intake-val" :class="{ 'danger-text': isOverLimit }">
            {{ displayConsumed }} <small>{{ unit }}</small>
          </span>
          <span class="limit-val">/ {{ displayLimit }} {{ unit }} limit</span>
        </div>
        <div class="summary-status">
          <span v-if="isOverLimit" class="status-tag danger-tag">
            ⚠️ {{ displayConsumed - displayLimit }} {{ unit }} Over Limit
          </span>
          <span v-else class="status-tag safe-tag">
            ✓ {{ displayLimit - displayConsumed }} {{ unit }} Under Limit
          </span>
        </div>
      </div>

      <!-- Logged Events List -->
      <div class="events-section">
        <h3 class="events-heading">
          Logged Intake Events ({{ report?.events?.length || 0 }})
        </h3>
        <ul v-if="report?.events && report.events.length > 0" class="event-list">
          <li v-for="(event, idx) in report.events" :key="event.id || idx" class="event-row">
            <div class="event-info">
              <span class="event-name">
                {{ event.event_type === 'manual_intake' ? 'Manual Intake' : event.event_type.replace(/_/g, ' ') }}
              </span>
              <span class="event-time">{{ formatEventTime(event.occurred_at) }}</span>
            </div>
            <span v-if="getEventVolume(event)" class="event-volume">
              {{ getEventVolume(event) }}
            </span>
            <span v-else-if="event.payload?.symptom" class="event-symptom">
              {{ event.payload.symptom }}
            </span>
          </li>
        </ul>
        <p v-else class="no-events-text">No intake logged on this day.</p>
      </div>

      <p v-if="summary" class="summary-note">{{ summary }}</p>
    </div>
  </section>
</template>

<style scoped>
.daily-report-card {
  padding: 18px;
  background: white;
  border-radius: 14px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #e2e8f0;
  border-top: 4px solid #00CFFF;
  margin-bottom: 16px;
}

.report-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.header-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  background: #e0f2fe;
  color: #007BFF;
  display: flex;
  align-items: center;
  justify-content: center;
}

.report-title {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: #141414;
}

.report-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

.intake-summary-box {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  padding: 14px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.warning-box {
  background: #fef2f2;
  border-color: #fecaca;
}

.summary-numbers {
  display: flex;
  align-items: baseline;
  gap: 6px;
}

.intake-val {
  font-size: 1.75rem;
  font-weight: 800;
  color: #007BFF;
  line-height: 1;
}

.intake-val small {
  font-size: 1rem;
  font-weight: 600;
}

.limit-val {
  font-size: 0.85rem;
  color: #64748b;
  font-weight: 600;
}

.status-tag {
  font-size: 0.75rem;
  font-weight: 700;
  padding: 4px 8px;
  border-radius: 6px;
}

.safe-tag {
  background: #dcfce7;
  color: #15803d;
}

.danger-tag {
  background: #fee2e2;
  color: #b91c1c;
}

.danger-text {
  color: #ef4444 !important;
}

.events-heading {
  font-size: 0.85rem;
  font-weight: 700;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 10px 0;
}

.event-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.event-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #f1f5f9;
}

.event-info {
  display: flex;
  flex-direction: column;
}

.event-name {
  font-size: 0.85rem;
  font-weight: 600;
  color: #1e293b;
  text-transform: capitalize;
}

.event-time {
  font-size: 0.7rem;
  color: #94a3b8;
}

.event-volume {
  font-size: 0.9rem;
  font-weight: 700;
  color: #007BFF;
}

.event-symptom {
  font-size: 0.8rem;
  font-weight: 600;
  color: #ef4444;
}

.no-events-text {
  font-size: 0.85rem;
  color: #94a3b8;
  font-style: italic;
  margin: 0;
}

.summary-note {
  margin-top: 14px;
  font-size: 0.85rem;
  color: #64748b;
  border-top: 1px solid #f1f5f9;
  padding-top: 10px;
}

.loading-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 24px 0;
  gap: 8px;
  color: #94a3b8;
}

.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid #e2e8f0;
  border-top-color: #007BFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Dark mode */
html.dark .daily-report-card {
  background: #141414;
  border-color: #333333;
}

html.dark .report-title {
  color: #f8fafc;
}

html.dark .report-subtitle {
  color: #94a3b8;
}

html.dark .header-icon {
  background: #1e293b;
  color: #00CFFF;
}

html.dark .intake-summary-box {
  background: #1e1e1e;
  border-color: #333333;
}

html.dark .warning-box {
  background: #2a1215;
  border-color: #7f1d1d;
}

html.dark .event-row {
  background: #1e1e1e;
  border-color: #333333;
}

html.dark .event-name {
  color: #f8fafc;
}

html.dark .event-volume {
  color: #00CFFF;
}

html.dark .limit-val {
  color: #94a3b8;
}
</style>
