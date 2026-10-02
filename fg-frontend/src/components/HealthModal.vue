<script setup>
import { ref, inject } from 'vue';
import api from '../services/api';
import { useAuth } from '../composables/useAuth';

const props = defineProps({
  isOpen: Boolean
});

const emit = defineEmits(['close']);
const showAlert = inject('showAlert');
const refreshDashboardTrigger = inject('refreshDashboardTrigger');

const { userProfile } = useAuth();
const predefinedSymptoms = [
  'Shortness of breath',
  'Swelling in ankles',
  'Rapid weight gain',
  'Fatigue',
  'Dizziness'
];

const selectedSymptom = ref('');
const customSymptom = ref('');
const isSubmitting = ref(false);

const selectSymptom = (symptom) => {
  selectedSymptom.value = symptom;
  customSymptom.value = '';
};

const submitSymptom = async () => {
  const symptomToLog = customSymptom.value.trim() || selectedSymptom.value;
  if (!symptomToLog) return;
  
  isSubmitting.value = true;
  try {
    const uid = userProfile.value?.uid || "default_user";
    await api.intake.post('/intake/symptom', {
      user_id: uid,
      symptom: symptomToLog
    });
    
    if (refreshDashboardTrigger) {
      refreshDashboardTrigger.value++;
    }
    
    showAlert(`Logged symptom: ${symptomToLog}`, "success");
    closeModal();
  } catch (error) {
    console.error("Failed to log symptom", error);
    showAlert("Failed to log symptom.", "error");
  } finally {
    isSubmitting.value = false;
  }
};

const closeModal = () => {
  selectedSymptom.value = '';
  customSymptom.value = '';
  emit('close');
};
</script>

<template>
  <div v-if="isOpen" class="modal-overlay" @click.self="closeModal">
    <div class="modal-content">
      <div class="modal-header">
        <h2>Log a Symptom</h2>
        <button class="close-btn" @click="closeModal">&times;</button>
      </div>

      <div class="symptom-list">
        <button 
          v-for="symptom in predefinedSymptoms" 
          :key="symptom"
          class="symptom-btn"
          :class="{ active: selectedSymptom === symptom && !customSymptom }"
          @click="selectSymptom(symptom)"
        >
          {{ symptom }}
        </button>
      </div>

      <div class="custom-input-group">
        <label>Or enter a custom symptom:</label>
        <input 
          type="text" 
          v-model="customSymptom" 
          placeholder="Type here..." 
          @focus="selectedSymptom = ''"
        />
      </div>

      <button 
        class="submit-btn" 
        :disabled="isSubmitting || (!selectedSymptom && !customSymptom.trim())"
        @click="submitSymptom"
      >
        {{ isSubmitting ? 'Logging...' : 'Log Symptom' }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.modal-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 100;
  animation: fadeIn 0.2s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.modal-content {
  background: white;
  width: 90%;
  max-width: 320px;
  max-height: 85vh;
  overflow-y: auto;
  border-radius: 20px;
  padding: 24px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.2);
  animation: scaleUp 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

@keyframes scaleUp {
  from { transform: scale(0.9); opacity: 0; }
  to { transform: scale(1); opacity: 1; }
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.modal-header h2 {
  margin: 0;
  font-size: 1.25rem;
  color: #0A0A0A;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  color: #666666;
  cursor: pointer;
}

.symptom-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
  margin-bottom: 20px;
}

.symptom-btn {
  padding: 10px 14px;
  background: #f1f5f9;
  border: 1px solid #C0C0C0;
  border-radius: 12px;
  font-size: 0.95rem;
  color: #333333;
  text-align: center;
  transition: all 0.2s;
  cursor: pointer;
}

.symptom-btn:hover {
  background: #e2e8f0;
}

.symptom-btn.active {
  background: #F8F9FA;
  border-color: #007BFF;
  color: #007BFF;
  font-weight: 600;
}

.custom-input-group {
  margin-bottom: 24px;
}

.custom-input-group label {
  display: block;
  font-size: 0.875rem;
  color: #666666;
  margin-bottom: 8px;
}

.custom-input-group input {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid #C0C0C0;
  border-radius: 12px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}

.custom-input-group input:focus {
  border-color: #007BFF;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1);
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: #007BFF;
  color: white;
  border: none;
  border-radius: 12px;
  font-size: 1.125rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #007BFF;
}

.submit-btn:disabled {
  background: #C0C0C0;
  cursor: not-allowed;
}

/* Dark Mode Overrides */
html.dark .modal-content {
  background: #141414;
  color: #FFFFFF;
}

html.dark .modal-header h2 {
  color: #FFFFFF;
}

html.dark .close-btn {
  color: #C0C0C0;
}
html.dark .close-btn:hover {
  background: #333333;
}

html.dark .symptom-btn {
  background: #111111;
  border-color: #333333;
  color: #C0C0C0;
}
html.dark .symptom-btn:hover {
  background: #333333;
}
html.dark .symptom-btn.selected {
  background: #007BFF;
  border-color: #007BFF;
  color: #FFFFFF;
}

html.dark .custom-input-group label {
  color: #C0C0C0;
}

html.dark .custom-input-group input {
  background: #111111;
  border-color: #333333;
  color: #FFFFFF;
}

html.dark .custom-input-group input:focus {
  border-color: #00CFFF;
}
</style>
