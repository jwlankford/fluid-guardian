<script setup>
import { ref, onMounted, onUnmounted } from 'vue';
import { Html5Qrcode } from "html5-qrcode";

const emit = defineEmits(['close', 'scan']);

const readerElement = ref(null);
let html5QrCode = null;
const isScanning = ref(false);
const scanError = ref('');

onMounted(async () => {
  try {
    html5QrCode = new Html5Qrcode("barcode-reader-container");
    
    await html5QrCode.start(
      { facingMode: "environment" },
      {
        fps: 10,
        qrbox: { width: 250, height: 150 }
      },
      (decodedText, decodedResult) => {
        // Success
        html5QrCode.stop();
        emit('scan', decodedText);
      },
      (errorMessage) => {
        // Ignored, happens when no barcode is in view
      }
    );
    isScanning.value = true;
  } catch (err) {
    console.error("Camera start error", err);
    scanError.value = "Could not start camera. Please ensure you have granted camera permissions.";
  }
});

onUnmounted(() => {
  if (html5QrCode && html5QrCode.isScanning) {
    html5QrCode.stop().catch(console.error);
  }
});

const closeScanner = () => {
  emit('close');
};
</script>

<template>
  <div class="scanner-modal-backdrop">
    <div class="scanner-modal">
      <div class="scanner-header">
        <h3>Scan Barcode</h3>
        <button @click="closeScanner" class="close-btn">
          <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" /></svg>
        </button>
      </div>
      
      <div class="scanner-body">
        <p v-if="scanError" class="error-text">{{ scanError }}</p>
        
        <!-- Scanner container -->
        <div id="barcode-reader-container" class="scanner-container"></div>
        
        <p class="instruction-text">Point camera at a product barcode (UPC/EAN)</p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.scanner-modal-backdrop {
  position: fixed;
  inset: 0;
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(4px);
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
}

.scanner-modal {
  background: white;
  width: 100%;
  max-width: 400px;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
}

.scanner-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e2e8f0;
}

.scanner-header h3 {
  margin: 0;
  font-size: 1.125rem;
  color: #0f172a;
}

.close-btn {
  background: transparent;
  border: none;
  color: #64748b;
  cursor: pointer;
  padding: 4px;
  border-radius: 8px;
}

.close-btn:hover {
  background: #f1f5f9;
  color: #0f172a;
}

.scanner-body {
  padding: 20px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.scanner-container {
  width: 100%;
  max-width: 300px;
  border-radius: 12px;
  overflow: hidden;
  margin-bottom: 16px;
}

.error-text {
  color: #ef4444;
  font-size: 0.875rem;
  text-align: center;
  margin-bottom: 12px;
}

.instruction-text {
  color: #64748b;
  font-size: 0.875rem;
  text-align: center;
  margin: 0;
}
</style>
