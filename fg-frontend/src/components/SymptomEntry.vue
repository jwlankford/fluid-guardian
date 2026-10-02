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
  padding: 8px;
}

button {
  padding: 8px 12px;
}
</style>
