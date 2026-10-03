<script setup>
import { ref, computed } from "vue";

const props = defineProps({
  days: {
    type: Array,
    default: () => [],
  },
  fluidLimit: {
    type: Number,
    default: 64, // in oz
  },
  measurementSystem: {
    type: String,
    default: "oz",
  },
  isLoading: {
    type: Boolean,
    default: false,
  },
  startDate: {
    type: String,
    default: "",
  },
  endDate: {
    type: String,
    default: "",
  },
});

// View Mode: 'combined', 'daily', or 'running'
const viewMode = ref("combined");
const activeIndex = ref(null);

const unit = computed(() => (props.measurementSystem === "ml" ? "mL" : "oz"));

// Convert limit to current unit
const currentLimit = computed(() => {
  return props.measurementSystem === "ml"
    ? Math.round(props.fluidLimit * 29.5735)
    : props.fluidLimit;
});

// Processed days with converted unit values
const chartData = computed(() => {
  if (!props.days || props.days.length === 0) return [];
  return props.days.map((d, index) => {
    const dailyVal =
      props.measurementSystem === "ml"
        ? Math.round(d.intake_ml)
        : Math.round(d.intake_ml / 29.5735);
    const runningVal =
      props.measurementSystem === "ml"
        ? Math.round(d.running_intake_ml)
        : Math.round(d.running_intake_ml / 29.5735);

    // Format date string for display (e.g., "10/02" or "Oct 2")
    const [year, month, day] = d.date.split("-");
    const dateObj = new Date(parseInt(year), parseInt(month) - 1, parseInt(day));
    const dayLabel = dateObj.toLocaleDateString("en-US", { month: "short", day: "numeric" });
    const weekday = dateObj.toLocaleDateString("en-US", { weekday: "short" });

    return {
      index,
      rawDate: d.date,
      dateLabel: dayLabel,
      weekday,
      dailyVal,
      runningVal,
      eventCount: d.event_count || (d.events ? d.events.length : 0),
      events: d.events || [],
      isOverLimit: dailyVal > currentLimit.value,
    };
  });
});

const formatEventTime = (isoString) => {
  if (!isoString) return "";
  const d = new Date(isoString);
  return isNaN(d.getTime())
    ? ""
    : d.toLocaleTimeString([], { hour: "numeric", minute: "2-digit" });
};

const formatEventVolume = (ml) => {
  if (ml === undefined || ml === null) return "";
  return props.measurementSystem === "ml"
    ? `${Math.round(ml)} mL`
    : `${Math.round(ml / 29.5735)} oz`;
};

// Summary calculations
const totalIntake = computed(() => {
  if (!chartData.value.length) return 0;
  return chartData.value[chartData.value.length - 1].runningVal;
});

const averageDaily = computed(() => {
  if (!chartData.value.length) return 0;
  return Math.round(totalIntake.value / chartData.value.length);
});

const overLimitCount = computed(() => {
  return chartData.value.filter((d) => d.isOverLimit).length;
});

// Chart Dimensions & Scales
const svgWidth = 330;
const svgHeight = 200;
const padding = { top: 24, right: 16, bottom: 32, left: 36 };
const innerWidth = svgWidth - padding.left - padding.right;
const innerHeight = svgHeight - padding.top - padding.bottom;

// Scales
const maxDailyVal = computed(() => {
  const maxDay = Math.max(0, ...chartData.value.map((d) => d.dailyVal));
  return Math.max(maxDay, currentLimit.value) * 1.15 || 10;
});

const maxRunningVal = computed(() => {
  const maxRun = Math.max(0, ...chartData.value.map((d) => d.runningVal));
  return (maxRun || 10) * 1.15;
});

// Scaling functions
const getX = (index) => {
  const count = chartData.value.length;
  if (count <= 1) return padding.left + innerWidth / 2;
  const step = innerWidth / count;
  return padding.left + index * step + step / 2;
};

const getBarX = (index) => {
  const count = chartData.value.length;
  const step = innerWidth / count;
  const barW = getBarWidth();
  return padding.left + index * step + (step - barW) / 2;
};

const getBarWidth = () => {
  const count = chartData.value.length;
  if (count <= 1) return 24;
  const step = innerWidth / count;
  return Math.max(8, Math.min(24, step * 0.65));
};

const getYDaily = (val) => {
  const max = maxDailyVal.value;
  return padding.top + innerHeight - (val / max) * innerHeight;
};

const getYRunning = (val) => {
  const max = viewMode.value === "daily" ? maxDailyVal.value : maxRunningVal.value;
  return padding.top + innerHeight - (val / max) * innerHeight;
};

// Limit line Y position
const limitY = computed(() => {
  return getYDaily(currentLimit.value);
});

// SVG Path for running cumulative total line
const runningLinePath = computed(() => {
  if (chartData.value.length === 0) return "";
  return chartData.value
    .map((d, i) => {
      const x = getX(i);
      const y = getYRunning(d.runningVal);
      return `${i === 0 ? "M" : "L"} ${x} ${y}`;
    })
    .join(" ");
});

// SVG Path for running cumulative total filled area
const runningAreaPath = computed(() => {
  if (chartData.value.length === 0) return "";
  const firstX = getX(0);
  const lastX = getX(chartData.value.length - 1);
  const baseY = padding.top + innerHeight;
  const linePart = chartData.value
    .map((d, i) => {
      const x = getX(i);
      const y = getYRunning(d.runningVal);
      return `L ${x} ${y}`;
    })
    .join(" ");
  return `M ${firstX} ${baseY} ${linePart} L ${lastX} ${baseY} Z`;
});

// Selected day details for tooltip/focus
const selectedDay = computed(() => {
  if (activeIndex.value !== null && chartData.value[activeIndex.value]) {
    return chartData.value[activeIndex.value];
  }
  return chartData.value[chartData.value.length - 1] || null;
});

const handlePointClick = (idx) => {
  activeIndex.value = idx;
};
</script>

<template>
  <div class="period-chart-container card">
    <!-- Header with Title & Mode Switcher -->
    <div class="chart-header">
      <div class="header-text">
        <h2 class="chart-title">Daily Fluid Intake</h2>
        <span class="chart-subtitle" v-if="startDate && endDate">
          {{ chartData[0]?.dateLabel }} – {{ chartData[chartData.length - 1]?.dateLabel }} ({{ chartData.length }} days)
        </span>
      </div>

      <!-- Mode selector toggles -->
      <div class="mode-toggles">
        <button
          type="button"
          :class="['mode-btn', { active: viewMode === 'combined' }]"
          @click="viewMode = 'combined'"
          title="Daily Bars with Running Cumulative Total"
        >
          Combined
        </button>
        <button
          type="button"
          :class="['mode-btn', { active: viewMode === 'daily' }]"
          @click="viewMode = 'daily'"
          title="Daily Fluid Intake"
        >
          Daily
        </button>
        <button
          type="button"
          :class="['mode-btn', { active: viewMode === 'running' }]"
          @click="viewMode = 'running'"
          title="Running Cumulative Total"
        >
          Running
        </button>
      </div>
    </div>

    <!-- Period Metrics Bar -->
    <div class="metrics-grid">
      <div class="metric-item">
        <span class="metric-label">Total Intake</span>
        <span class="metric-val">{{ totalIntake }} <small>{{ unit }}</small></span>
      </div>
      <div class="metric-item">
        <span class="metric-label">Daily Average</span>
        <span class="metric-val">{{ averageDaily }} <small>{{ unit }}/d</small></span>
      </div>
      <div class="metric-item">
        <span class="metric-label">Daily Limit</span>
        <span class="metric-val">{{ currentLimit }} <small>{{ unit }}</small></span>
      </div>
      <div class="metric-item">
        <span class="metric-label">Status</span>
        <span
          class="metric-val status-pill"
          :class="overLimitCount > 0 ? 'pill-warning' : 'pill-good'"
        >
          {{ overLimitCount > 0 ? `${overLimitCount}d Over` : 'Within Limit' }}
        </span>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="isLoading" class="chart-loading">
      <div class="loading-spinner"></div>
      <p>Loading intake data...</p>
    </div>

    <!-- Empty State -->
    <div v-else-if="chartData.length === 0" class="chart-empty">
      <svg width="40" height="40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
      </svg>
      <p>No intake data recorded for this period.</p>
    </div>

    <!-- Main SVG Chart -->
    <div v-else class="svg-wrapper">
      <svg
        class="period-svg"
        :viewBox="`0 0 ${svgWidth} ${svgHeight}`"
        preserveAspectRatio="xMidYMid meet"
      >
        <defs>
          <!-- Bar gradient normal -->
          <linearGradient id="barGradientNormal" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#00CFFF" />
            <stop offset="100%" stop-color="#007BFF" />
          </linearGradient>

          <!-- Bar gradient over limit -->
          <linearGradient id="barGradientOver" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#f87171" />
            <stop offset="100%" stop-color="#ef4444" />
          </linearGradient>

          <!-- Running Area gradient -->
          <linearGradient id="runningAreaGradient" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stop-color="#00CFFF" stop-opacity="0.35" />
            <stop offset="100%" stop-color="#007BFF" stop-opacity="0.02" />
          </linearGradient>
        </defs>

        <!-- Horizontal Grid Lines -->
        <g class="grid-lines">
          <line
            :x1="padding.left"
            :y1="padding.top"
            :x2="svgWidth - padding.right"
            :y2="padding.top"
          />
          <line
            :x1="padding.left"
            :y1="padding.top + innerHeight / 2"
            :x2="svgWidth - padding.right"
            :y2="padding.top + innerHeight / 2"
          />
          <line
            :x1="padding.left"
            :y1="padding.top + innerHeight"
            :x2="svgWidth - padding.right"
            :y2="padding.top + innerHeight"
          />
        </g>

        <!-- Fluid Limit Reference Line (shown in daily and combined modes) -->
        <g v-if="viewMode !== 'running'" class="limit-line-group">
          <line
            :x1="padding.left"
            :y1="limitY"
            :x2="svgWidth - padding.right"
            :y2="limitY"
            class="limit-line"
          />
          <text
            :x="svgWidth - padding.right"
            :y="limitY - 4"
            class="limit-text"
            text-anchor="end"
          >
            Limit: {{ currentLimit }} {{ unit }}
          </text>
        </g>

        <!-- Running Cumulative Area & Line (in running & combined modes) -->
        <g v-if="viewMode === 'running' || viewMode === 'combined'" class="running-group">
          <path :d="runningAreaPath" fill="url(#runningAreaGradient)" />
          <path
            :d="runningLinePath"
            class="running-line"
            :class="{ 'dimmed-line': viewMode === 'combined' }"
          />
        </g>

        <!-- Daily Bars (in daily and combined modes) -->
        <g v-if="viewMode === 'daily' || viewMode === 'combined'" class="bars-group">
          <rect
            v-for="(d, i) in chartData"
            :key="'bar-' + i"
            :x="getBarX(i)"
            :y="getYDaily(d.dailyVal)"
            :width="getBarWidth()"
            :height="Math.max(2, padding.top + innerHeight - getYDaily(d.dailyVal))"
            :rx="getBarWidth() / 3"
            :fill="d.isOverLimit ? 'url(#barGradientOver)' : 'url(#barGradientNormal)'"
            class="chart-bar"
            :class="{ active: activeIndex === i }"
            @click="handlePointClick(i)"
            @mouseenter="activeIndex = i"
          />
        </g>

        <!-- Running Line Data Points -->
        <g v-if="viewMode === 'running' || viewMode === 'combined'" class="running-points">
          <circle
            v-for="(d, i) in chartData"
            :key="'point-' + i"
            :cx="getX(i)"
            :cy="getYRunning(d.runningVal)"
            :r="activeIndex === i ? 5 : 3.5"
            class="running-point"
            :class="{ active: activeIndex === i }"
            @click="handlePointClick(i)"
            @mouseenter="activeIndex = i"
          />
        </g>

        <!-- X-Axis Date Labels -->
        <g class="x-axis">
          <template v-for="(d, i) in chartData" :key="'label-' + i">
            <!-- Show every label if <= 7 days, else alternate to prevent crowding -->
            <text
              v-if="chartData.length <= 7 || i % Math.ceil(chartData.length / 6) === 0 || i === chartData.length - 1"
              :x="getX(i)"
              :y="padding.top + innerHeight + 16"
              class="axis-label"
              text-anchor="middle"
            >
              {{ d.dateLabel }}
            </text>
          </template>
        </g>

        <!-- Y-Axis Ticks -->
        <g class="y-axis">
          <text
            :x="padding.left - 6"
            :y="padding.top + 4"
            class="axis-label"
            text-anchor="end"
          >
            {{ Math.round(viewMode === 'running' ? maxRunningVal : maxDailyVal) }}
          </text>
          <text
            :x="padding.left - 6"
            :y="padding.top + innerHeight / 2 + 4"
            class="axis-label"
            text-anchor="end"
          >
            {{ Math.round((viewMode === 'running' ? maxRunningVal : maxDailyVal) / 2) }}
          </text>
          <text
            :x="padding.left - 6"
            :y="padding.top + innerHeight"
            class="axis-label"
            text-anchor="end"
          >
            0
          </text>
        </g>
      </svg>
    </div>

    <!-- Active Day Detail Card / Legend -->
    <div v-if="selectedDay" class="day-detail-card">
      <div class="detail-header">
        <span class="detail-date">{{ selectedDay.weekday }}, {{ selectedDay.dateLabel }}</span>
        <span
          class="badge"
          :class="selectedDay.isOverLimit ? 'badge-danger' : 'badge-safe'"
        >
          {{ selectedDay.isOverLimit ? 'Over Limit' : 'Within Limit' }}
        </span>
      </div>

      <div class="detail-stats">
        <div class="stat-col">
          <span class="stat-title">Daily Intake</span>
          <span class="stat-number" :class="{ 'danger-color': selectedDay.isOverLimit }">
            {{ selectedDay.dailyVal }} <small>{{ unit }}</small>
          </span>
        </div>
        <div class="stat-col">
          <span class="stat-title">Running Total</span>
          <span class="stat-number running-color">
            {{ selectedDay.runningVal }} <small>{{ unit }}</small>
          </span>
        </div>
        <div class="stat-col">
          <span class="stat-title">Limit Difference</span>
          <span
            class="stat-number"
            :class="selectedDay.dailyVal > currentLimit ? 'danger-color' : 'safe-color'"
          >
            {{ selectedDay.dailyVal > currentLimit ? '+' : '' }}{{ selectedDay.dailyVal - currentLimit }}
            <small>{{ unit }}</small>
          </span>
        </div>
      </div>

      <!-- Logged Events for Selected Day -->
      <div class="detail-events-section">
        <h4 class="detail-events-title">
          Events on {{ selectedDay.dateLabel }} ({{ selectedDay.events?.length || 0 }})
        </h4>
        <ul v-if="selectedDay.events && selectedDay.events.length > 0" class="detail-event-list">
          <li v-for="(ev, eIdx) in selectedDay.events" :key="ev.id || eIdx" class="detail-event-row">
            <div class="event-meta">
              <span class="event-type-badge">
                {{ ev.event_type === 'manual_intake' ? 'Manual Intake' : ev.event_type.replace(/_/g, ' ') }}
              </span>
              <span class="event-timestamp">{{ formatEventTime(ev.occurred_at) }}</span>
            </div>
            <div class="event-val">
              <span v-if="ev.payload?.volume_ml !== undefined && ev.payload?.volume_ml !== null" class="event-volume-text">
                {{ formatEventVolume(ev.payload.volume_ml) }}
              </span>
              <span v-else-if="ev.payload?.symptom" class="event-symptom-text">
                ⚠️ {{ ev.payload.symptom }}
              </span>
            </div>
          </li>
        </ul>
        <p v-else class="detail-no-events">No fluid events logged on this day.</p>
      </div>
    </div>

    <!-- Visual Legend -->
    <div class="chart-legend">
      <div class="legend-item" v-if="viewMode !== 'running'">
        <span class="legend-color-box bar-color"></span>
        <span>Daily Intake</span>
      </div>
      <div class="legend-item" v-if="viewMode !== 'daily'">
        <span class="legend-line running-color-line"></span>
        <span>Running Cumulative</span>
      </div>
      <div class="legend-item" v-if="viewMode !== 'running'">
        <span class="legend-line limit-color-line"></span>
        <span>Daily Limit</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.period-chart-container {
  padding: 16px;
  background: #ffffff;
  border-radius: 16px;
  border: 1px solid #e2e8f0;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  margin-bottom: 16px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 8px;
  margin-bottom: 14px;
}

.chart-title {
  font-size: 1.125rem;
  font-weight: 700;
  color: #141414;
  margin: 0 0 2px 0;
}

.chart-subtitle {
  font-size: 0.75rem;
  color: #64748b;
  font-weight: 500;
}

/* Mode toggles */
.mode-toggles {
  display: flex;
  background: #f1f5f9;
  border-radius: 8px;
  padding: 2px;
  gap: 2px;
}

.mode-btn {
  padding: 4px 8px;
  border: none;
  background: transparent;
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.mode-btn.active {
  background: #ffffff;
  color: #007BFF;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.08);
}

/* Metrics Grid */
.metrics-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  background: #f8fafc;
  padding: 10px;
  border-radius: 10px;
  border: 1px solid #f1f5f9;
  margin-bottom: 14px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.metric-label {
  font-size: 0.65rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  margin-bottom: 2px;
  letter-spacing: 0.03em;
}

.metric-val {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0f172a;
}

.metric-val small {
  font-size: 0.65rem;
  font-weight: 600;
  color: #64748b;
}

.status-pill {
  font-size: 0.7rem;
  padding: 2px 6px;
  border-radius: 6px;
}

.pill-good {
  background: #dcfce7;
  color: #166534;
}

.pill-warning {
  background: #fee2e2;
  color: #991b1b;
}

/* SVG Styles */
.svg-wrapper {
  width: 100%;
  position: relative;
}

.period-svg {
  width: 100%;
  height: auto;
  overflow: visible;
}

.grid-lines line {
  stroke: #f1f5f9;
  stroke-width: 1;
}

.limit-line {
  stroke: #ef4444;
  stroke-width: 1.5;
  stroke-dasharray: 4 3;
}

.limit-text {
  font-size: 8px;
  fill: #ef4444;
  font-weight: 600;
}

.running-line {
  fill: none;
  stroke: #007BFF;
  stroke-width: 2.5;
  stroke-linecap: round;
  stroke-linejoin: round;
  filter: drop-shadow(0 2px 4px rgba(0, 123, 255, 0.2));
}

.running-line.dimmed-line {
  stroke: #0284c7;
  stroke-width: 2;
}

.chart-bar {
  cursor: pointer;
  transition: opacity 0.2s, transform 0.2s;
}

.chart-bar:hover,
.chart-bar.active {
  opacity: 0.85;
  filter: brightness(1.1);
}

.running-point {
  fill: #ffffff;
  stroke: #007BFF;
  stroke-width: 2;
  cursor: pointer;
  transition: r 0.2s, stroke-width 0.2s;
}

.running-point:hover,
.running-point.active {
  stroke: #00CFFF;
  stroke-width: 3;
}

.axis-label {
  font-size: 8.5px;
  fill: #64748b;
  font-family: inherit;
  font-weight: 500;
}

/* Loading & Empty */
.chart-loading,
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 36px 16px;
  color: #94a3b8;
  text-align: center;
  gap: 8px;
}

.loading-spinner {
  width: 28px;
  height: 28px;
  border: 3px solid #e2e8f0;
  border-top-color: #007BFF;
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* Detail Card */
.day-detail-card {
  margin-top: 14px;
  padding: 10px 14px;
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.detail-date {
  font-size: 0.8rem;
  font-weight: 700;
  color: #1e293b;
}

.badge {
  font-size: 0.65rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 4px;
  text-transform: uppercase;
}

.badge-safe {
  background: #dcfce7;
  color: #15803d;
}

.badge-danger {
  background: #fee2e2;
  color: #b91c1c;
}

.detail-stats {
  display: flex;
  justify-content: space-between;
  gap: 12px;
}

.stat-col {
  display: flex;
  flex-direction: column;
}

.stat-title {
  font-size: 0.65rem;
  color: #64748b;
  margin-bottom: 2px;
}

.stat-number {
  font-size: 0.95rem;
  font-weight: 800;
  color: #0f172a;
}

.stat-number small {
  font-size: 0.65rem;
  font-weight: 600;
  color: #64748b;
}

.danger-color {
  color: #ef4444 !important;
}

.safe-color {
  color: #16a34a !important;
}

.running-color {
  color: #0284c7 !important;
}

/* Legend */
.chart-legend {
  display: flex;
  justify-content: center;
  gap: 16px;
  margin-top: 12px;
  font-size: 0.7rem;
  font-weight: 600;
  color: #64748b;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
}

.legend-color-box {
  width: 10px;
  height: 10px;
  border-radius: 2px;
}

.bar-color {
  background: linear-gradient(to top, #007BFF, #00CFFF);
}

.legend-line {
  width: 14px;
  height: 2px;
  border-radius: 1px;
}

.running-color-line {
  background: #007BFF;
}

.limit-color-line {
  background: #ef4444;
  border-top: 1px dashed #ef4444;
  height: 0;
}

/* Dark Mode Overrides */
html.dark .period-chart-container {
  background: #141414;
  border-color: #333333;
}

html.dark .chart-title {
  color: #f8fafc;
}

html.dark .chart-subtitle {
  color: #94a3b8;
}

html.dark .mode-toggles {
  background: #222222;
}

html.dark .mode-btn {
  color: #94a3b8;
}

html.dark .mode-btn.active {
  background: #333333;
  color: #00CFFF;
}

html.dark .metrics-grid {
  background: #1e1e1e;
  border-color: #333333;
}

html.dark .metric-label {
  color: #94a3b8;
}

html.dark .metric-val {
  color: #f8fafc;
}

html.dark .metric-val small {
  color: #94a3b8;
}

html.dark .grid-lines line {
  stroke: #262626;
}

html.dark .axis-label {
  fill: #94a3b8;
}

html.dark .day-detail-card {
  background: #1e1e1e;
  border-color: #333333;
}

html.dark .detail-date {
  color: #f8fafc;
}

html.dark .stat-title {
  color: #94a3b8;
}

html.dark .stat-number {
  color: #f8fafc;
}

html.dark .stat-number small {
  color: #94a3b8;
}

html.dark .chart-legend {
  color: #94a3b8;
}

html.dark .running-point {
  fill: #141414;
  stroke: #00CFFF;
}

html.dark .pill-good {
  background: #064e3b;
  color: #6ee7b7;
}

html.dark .pill-warning {
  background: #7f1d1d;
  color: #fca5a5;
}

.detail-events-section {
  margin-top: 14px;
  padding-top: 12px;
  border-top: 1px solid #e2e8f0;
}

.detail-events-title {
  font-size: 0.8rem;
  font-weight: 700;
  color: #475569;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  margin: 0 0 8px 0;
}

.detail-event-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-event-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 10px;
  background: #f8fafc;
  border-radius: 8px;
  border: 1px solid #e2e8f0;
}

.event-meta {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.event-type-badge {
  font-size: 0.8rem;
  font-weight: 600;
  color: #1e293b;
  text-transform: capitalize;
}

.event-timestamp {
  font-size: 0.7rem;
  color: #94a3b8;
}

.event-volume-text {
  font-size: 0.85rem;
  font-weight: 700;
  color: #007BFF;
}

.event-symptom-text {
  font-size: 0.8rem;
  font-weight: 600;
  color: #ef4444;
}

.detail-no-events {
  font-size: 0.8rem;
  color: #94a3b8;
  font-style: italic;
  margin: 4px 0 0 0;
}

html.dark .detail-events-section {
  border-top-color: #333333;
}

html.dark .detail-events-title {
  color: #94a3b8;
}

html.dark .detail-event-row {
  background: #262626;
  border-color: #333333;
}

html.dark .event-type-badge {
  color: #f8fafc;
}

html.dark .event-volume-text {
  color: #00CFFF;
}

html.dark .badge-safe {
  background: #064e3b;
  color: #6ee7b7;
}

html.dark .badge-danger {
  background: #7f1d1d;
  color: #fca5a5;
}
</style>
