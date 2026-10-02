<script setup>
import { inject, ref, watch, computed } from 'vue';

const isDarkMode = inject('isDarkMode');
const toggleTheme = inject('toggleTheme');

// Reset mode: 'daily' or 'period'
const resetMode = inject('resetMode');

watch(resetMode, (newVal) => {
  localStorage.setItem('resetMode', newVal);
});

const handleThemeToggle = () => {
  toggleTheme();
};

const handleResetToggle = () => {
  resetMode.value = resetMode.value === 'daily' ? 'period' : 'daily';
};

const statusBadgeText = computed(() => {
  return resetMode.value === 'daily' ? 'Daily' : 'By Period';
});

const measurementSystem = inject('measurementSystem');

watch(measurementSystem, (newVal) => {
  localStorage.setItem('measurementSystem', newVal);
});

const handleMeasurementToggle = () => {
  measurementSystem.value = measurementSystem.value === 'oz' ? 'ml' : 'oz';
};

const fluidLimit = inject('fluidLimit');

watch(fluidLimit, (newVal) => {
  localStorage.setItem('fluidLimit', newVal);
});

const displayLimit = computed(() => {
  return measurementSystem.value === 'ml' ? Math.round(fluidLimit.value * 29.5735) : fluidLimit.value;
});
const displayUnit = computed(() => {
  return measurementSystem.value === 'ml' ? 'mL' : 'oz';
});
</script>

<template>
  <section class="preferences-page">
    <div class="page-header">
      <h1 class="page-title">Preferences</h1>
    </div>

    <div class="card prefs-card">
      <div class="pref-item limit-item">
        <div class="pref-info" style="flex: 1;">
          <h3>Fluid Limit</h3>
          <p>Set your daily maximum restriction</p>
          <div class="slider-container">
            <input 
              type="range" 
              min="20" 
              max="72" 
              step="1" 
              v-model.number="fluidLimit"
              class="limit-slider" 
            />
            <span class="status-badge" style="margin-top: 0; margin-left: 12px;">
              {{ displayLimit }} {{ displayUnit }}
            </span>
          </div>
        </div>
      </div>



      <div class="pref-item">
        <div class="pref-info">
          <h3>Dark Mode</h3>
          <p>Switch between light and dark themes</p>
        </div>
        <button class="toggle-btn" :class="{ active: isDarkMode }" @click="handleThemeToggle">
          <div class="toggle-knob"></div>
        </button>
      </div>



      <div class="pref-item">
        <div class="pref-info">
          <h3>Reset Schedule</h3>
          <p>When to reset fluid tracking totals</p>
          <span class="status-badge">{{ statusBadgeText }}</span>
        </div>
        <button class="toggle-btn" :class="{ active: resetMode === 'period' }" @click="handleResetToggle">
          <div class="toggle-knob"></div>
        </button>
      </div>



      <div class="pref-item">
        <div class="pref-info">
          <h3>Measurement System</h3>
          <p>Switch between Ounces and Milliliters</p>
          <span class="status-badge">{{ measurementSystem === 'oz' ? 'Ounces (oz)' : 'Milliliters (mL)' }}</span>
        </div>
        <button class="toggle-btn" :class="{ active: measurementSystem === 'ml' }" @click="handleMeasurementToggle">
          <div class="toggle-knob"></div>
        </button>
      </div>
    </div>
  </section>
</template>

<style scoped>
.preferences-page {
  padding: 0.5rem;
  padding-bottom: 0px;
  max-width: 600px;
  margin: 0 auto;
}

.page-header {
  margin-bottom: 1.5rem;
}

.page-title {
  color: #007BFF;
  font-size: 1.75rem;
  font-weight: 800;
  margin: 0;
}

.prefs-card {
  display: flex;
  flex-direction: column;
  padding: 24px;
}

.pref-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 0;
}

.pref-info h3 {
  margin: 0 0 4px;
  font-size: 1.1rem;
}

.pref-info p {
  margin: 0;
  font-size: 0.85rem;
  color: #666666;
}

.status-badge {
  display: inline-block;
  margin-top: 8px;
  padding: 4px 8px;
  background: #e0f2fe;
  color: #007BFF;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: bold;
}

html.dark .status-badge {
  background: #111111;
  color: #00CFFF;
  border: 1px solid #333333;
}


.slider-container {
  display: flex;
  align-items: center;
  margin-top: 12px;
}

.limit-slider {
  flex: 1;
  cursor: pointer;
  accent-color: #007BFF;
}

/* Custom Toggle Switch */
.toggle-btn {
  width: 50px;
  height: 28px;
  background: #cbd5e1;
  border-radius: 14px;
  border: none;
  position: relative;
  cursor: pointer;
  transition: background 0.3s;
}

.toggle-btn.active {
  background: #007BFF;
}

.toggle-knob {
  width: 22px;
  height: 22px;
  background: white;
  border-radius: 50%;
  position: absolute;
  top: 3px;
  left: 3px;
  transition: transform 0.3s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.2);
}

.toggle-btn.active .toggle-knob {
  transform: translateX(22px);
}

html.dark .toggle-btn {
  background: #444444;
}

html.dark .toggle-btn.active {
  background: #007BFF;
}
</style>
