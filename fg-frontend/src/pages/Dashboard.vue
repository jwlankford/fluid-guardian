<script setup>
import { ref, computed } from "vue";
import { useAuth } from "../composables/useAuth.js";

const { userProfile } = useAuth();

// MOCK DATA
const fluidConsumed = ref(45); // Current consumed 
const fluidLimit = ref(32); // Doctor's limit
const symptoms = ref(["Shortness of breath", "Swelling in ankles"]);

// Calculate risk percentage
const riskPercentage = computed(() => {
  const percent = (fluidConsumed.value / fluidLimit.value) * 100;
  return Math.min(percent, 100); // Cap at 100% for the visual bar
});

// Calculate how much of the gradient to cover up with gray
const maskWidth = computed(() => {
  return 100 - riskPercentage.value;
});

// Determine Risk Label
const riskLabel = computed(() => {
  if (fluidConsumed.value < fluidLimit.value * 0.75) return "Low Risk";
  if (fluidConsumed.value < fluidLimit.value) return "Warning";
  return "High Risk (Critical)";
});
</script>

<template>
  <section class="dashboard-page">
    <h1 class="page-title">Dashboard</h1>
    
    <div class="dashboard-cards">
      <!-- FLUID INTAKE CARD -->
      <div class="card fluid-card">
        <div class="card-header">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z" /></svg>
          <h2>Fluid Intake</h2>
        </div>
        
        <div class="intake-numbers">
          <span class="consumed" :class="{ 'danger-text': fluidConsumed > fluidLimit }">
            {{ fluidConsumed }}<span class="unit">oz</span>
          </span>
          <span class="divider">/</span>
          <span class="limit">{{ fluidLimit }} oz limit</span>
        </div>
        
        <p v-if="fluidConsumed > fluidLimit" class="over-limit-warning">
          You are {{ fluidConsumed - fluidLimit }} oz over your daily restriction!
        </p>
      </div>

      <!-- RISK LEVEL CARD -->
      <div class="card risk-card">
        <div class="card-header">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
          <h2>Risk Level: <span :class="{'danger-text': fluidConsumed >= fluidLimit}">{{ riskLabel }}</span></h2>
        </div>
        
        <div class="risk-bar-wrapper">
          <!-- The full gradient track (Green -> Yellow -> Red) -->
          <div class="risk-gradient">
            <!-- The gray mask that hides the unused portion -->
            <div class="risk-mask" :style="{ width: `${maskWidth}%` }"></div>
            
            <!-- A marker showing exact position -->
            <div class="risk-marker" :style="{ left: `${riskPercentage}%` }"></div>
          </div>
        </div>
        <div class="risk-labels">
          <span>Safe</span>
          <span>Danger</span>
        </div>
      </div>

      <!-- SYMPTOMS CARD -->
      <div class="card symptoms-card">
        <div class="card-header">
          <svg class="icon" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
          <h2>Logged Symptoms</h2>
        </div>
        <ul v-if="symptoms.length" class="symptom-list">
          <li v-for="(symptom, index) in symptoms" :key="index" class="symptom-item">
            {{ symptom }}
          </li>
        </ul>
        <p v-else class="empty-text">No symptoms logged today.</p>
      </div>

    </div>
  </section>
</template>

<style scoped>
.dashboard-page {
  padding: 1rem;
  padding-bottom: 5rem;
  max-width: 600px;
  margin: 0 auto;
}

.page-title {
  color: #0369a1;
  font-size: 1.75rem;
  font-weight: 800;
  margin-top: 0;
  margin-bottom: 1.5rem;
}

.dashboard-cards {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.card {
  background: #ffffff;
  border-radius: 16px;
  padding: 20px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
  border: 1px solid #e2e8f0;
}

.card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 16px;
}

.card-header h2 {
  margin: 0;
  font-size: 1.125rem;
  font-weight: 700;
  color: #1e293b;
}

.icon {
  width: 24px;
  height: 24px;
  color: #0284c7;
}

/* FLUID INTAKE STYLES */
.intake-numbers {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.consumed {
  font-size: 3.5rem;
  font-weight: 900;
  color: #0284c7;
  line-height: 1;
}

.danger-text {
  color: #ef4444 !important;
}

.unit {
  font-size: 1.25rem;
  font-weight: 600;
  margin-left: 4px;
}

.divider {
  font-size: 2rem;
  color: #94a3b8;
  font-weight: 300;
}

.limit {
  font-size: 1.25rem;
  color: #64748b;
  font-weight: 600;
}

.over-limit-warning {
  margin-top: 12px;
  margin-bottom: 0;
  padding: 8px 12px;
  background: #fef2f2;
  color: #b91c1c;
  border-radius: 8px;
  font-weight: 600;
  font-size: 0.875rem;
  border: 1px solid #fecaca;
}

/* RISK BAR STYLES */
.risk-bar-wrapper {
  margin-top: 8px;
}

.risk-gradient {
  width: 100%;
  height: 24px;
  background: linear-gradient(to right, #4ade80, #facc15, #f87171, #ef4444);
  border-radius: 12px;
  display: flex;
  justify-content: flex-end; /* Push the mask to the right */
  position: relative;
  overflow: hidden;
  box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
}

.risk-mask {
  height: 100%;
  background-color: #e2e8f0; /* Gray covers the unused portion */
  transition: width 0.5s ease-out;
}

.risk-marker {
  position: absolute;
  top: 0;
  bottom: 0;
  width: 4px;
  background: #1e293b;
  border-radius: 2px;
  transform: translateX(-50%);
  z-index: 10;
  box-shadow: 0 0 0 2px rgba(255,255,255,0.5);
}

.risk-labels {
  display: flex;
  justify-content: space-between;
  margin-top: 6px;
  font-size: 0.75rem;
  font-weight: 600;
  color: #64748b;
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

/* SYMPTOMS STYLES */
.symptom-list {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.symptom-item {
  background: #f8fafc;
  border: 1px solid #e2e8f0;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  color: #334155;
  display: flex;
  align-items: center;
}

.symptom-item::before {
  content: "•";
  color: #ef4444;
  font-size: 1.5rem;
  margin-right: 8px;
  line-height: 0;
}

.empty-text {
  color: #94a3b8;
  font-style: italic;
  margin: 0;
}
</style>
