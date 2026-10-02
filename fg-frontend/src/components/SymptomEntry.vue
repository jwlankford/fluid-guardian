<script setup>
import { ref } from "vue";

const symptom = ref("");
const emit = defineEmits(["submit"]);

function submitSymptom() {
  const value = symptom.value.trim();
  if (!value) return;

  emit("submit", value);
  symptom.value = "";
}
</script>

<template>
  <form class="symptom-entry" @submit.prevent="submitSymptom">
    <label for="symptom">Record a symptom</label>
    <div>
      <input id="symptom" v-model="symptom" name="symptom" required />
      <button type="submit">Save</button>
    </div>
  </form>
</template>

<style scoped>
.symptom-entry {
  display: grid;
  gap: 8px;
}

.symptom-entry div {
  display: flex;
  gap: 8px;
}

input {
  min-width: 0;
  flex: 1;
  padding: 8px 12px;
  border: 1px solid #7dd3fc;
  border-radius: 6px;
  outline: none;
}

input:focus {
  border-color: #0284c7;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.2);
}

button {
  padding: 8px 16px;
  background-color: #0284c7;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  transition: background-color 0.2s;
}

button:hover {
  background-color: #0369a1;
}
</style>
