<script setup>
import { ref } from "vue";
import DailyReport from "../components/DailyReport.vue";
import FluidEntryCard from "../components/FluidEntryCard.vue";
import ItemUpload from "../components/ItemUpload.vue";
import RiskIndicator from "../components/RiskIndicator.vue";
import SymptomEntry from "../components/SymptomEntry.vue";

const symptoms = ref([]);
</script>

<template>
  <section>
    <h1>Dashboard</h1>
    <div class="dashboard-grid">
      <FluidEntryCard />
      <RiskIndicator />
      <DailyReport />
      <ItemUpload />
    </div>
    <section class="symptoms">
      <h2>Symptoms</h2>
      <SymptomEntry @submit="symptoms.push($event)" />
      <ul v-if="symptoms.length">
        <li v-for="(symptom, index) in symptoms" :key="`${symptom}-${index}`">
          {{ symptom }}
        </li>
      </ul>
    </section>
  </section>
</template>

<style scoped>
.dashboard-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 16px;
}

h1, h2 {
  color: #0369a1;
}

.symptoms {
  margin-top: 24px;
  padding: 20px;
  border-radius: 10px;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.1), 0 2px 4px -1px rgba(2, 132, 199, 0.06);
  border-top: 4px solid #7dd3fc;
}
</style>
