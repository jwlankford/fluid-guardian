<script setup>
import { ref, computed, onMounted, onUnmounted, inject } from 'vue';
import api from '../services/api.js';
import { useAuth } from '../composables/useAuth.js';
import BarcodeScanner from '../components/BarcodeScanner.vue';

const showAlert = inject('showAlert');
const resetMode = inject('resetMode');
const isDaily = computed(() => resetMode.value === 'daily');
const fluidLimit = inject('fluidLimit');
const { isLoggedIn, userProfile } = useAuth();
const currentOz = ref(0);
const isSubmitting = ref(false);
const isScannerOpen = ref(false);
const isLookingUp = ref(false);

const handleBarcodeScan = async (barcode) => {
  isScannerOpen.value = false;
  isLookingUp.value = true;
  
  try {
    const res = await fetch(`https://world.openfoodfacts.org/api/v0/product/${barcode}.json`);
    const data = await res.json();
    
    if (data.status === 1 && data.product) {
      let ml = parseFloat(data.product.product_quantity);
      
      if (!ml && data.product.quantity) {
        const qtyStr = data.product.quantity.toLowerCase();
        const match = qtyStr.match(/([\d.]+)\s*(ml|l|fl oz|oz)/);
        if (match) {
          const val = parseFloat(match[1]);
          const unit = match[2];
          if (unit === 'l') ml = val * 1000;
          else if (unit === 'fl oz' || unit === 'oz') ml = val * 29.5735;
          else ml = val;
        }
      }
      
      if (ml) {
        const oz = Math.round(ml / 29.5735);
        currentOz.value = oz;
        const ozMod = currentOz.value % fluidLimit.value;
        lastAngle = ozMod * (360 / fluidLimit.value);
        const amt = measurementSystem.value === 'ml' ? Math.round(ml) : oz;
        alert(`Found ${data.product.product_name || 'Product'}!\nLoaded ${amt} ${displayUnit.value}.`);
      } else {
        alert(`Found ${data.product.product_name || 'Product'}, but couldn't determine its volume!`);
      }
    } else {
      alert("Product not found in Open Food Facts database.");
    }
  } catch (e) {
    console.error("Barcode lookup failed:", e);
    alert("Error looking up product.");
  } finally {
    isLookingUp.value = false;
  }
};

const setCupLevel = (i) => {
  currentOz.value = i * 8;
  const ozMod = currentOz.value % fluidLimit.value;
  lastAngle = ozMod * (360 / fluidLimit.value);
};

// Circle Slider Logic
const sliderRef = ref(null);
const isDragging = ref(false);
const center = { x: 150, y: 150 };
const radius = 120;
let lastAngle = 0;

const getAngle = (x, y) => {
  const dx = x - center.x;
  const dy = y - center.y;
  let angle = Math.atan2(dy, dx) * (180 / Math.PI);
  if (angle < 0) angle += 360;
  return angle;
};

const handlePointerDown = (e) => {
  if (!sliderRef.value) return;
  isDragging.value = true;
  const rect = sliderRef.value.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * 300;
  const y = ((e.clientY - rect.top) / rect.height) * 300;
  lastAngle = getAngle(x, y);
  
  // Also add global event listeners for drag and up
  window.addEventListener('pointermove', handlePointerMove);
  window.addEventListener('pointerup', handlePointerUp);
};

const handlePointerMove = (e) => {
  if (!isDragging.value || !sliderRef.value) return;
  const rect = sliderRef.value.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * 300;
  const y = ((e.clientY - rect.top) / rect.height) * 300;
  
  const currentAngle = getAngle(x, y);
  let diff = currentAngle - lastAngle;
  
  // Handle wraparound
  if (diff > 180) diff -= 360;
  else if (diff < -180) diff += 360;
  
  // 360 degrees = fluidLimit ounces
  const degreesPerOz = 360 / fluidLimit.value;
  
  if (Math.abs(diff) >= degreesPerOz) {
    const ticks = Math.floor(Math.abs(diff) / degreesPerOz) * Math.sign(diff);
    const newOz = Math.max(0, Math.min(fluidLimit.value, currentOz.value + ticks));
    
    if (newOz !== currentOz.value) {
      const actualTicks = newOz - currentOz.value;
      currentOz.value = newOz;
      lastAngle += actualTicks * degreesPerOz;
      
      // Normalize lastAngle
      if (lastAngle >= 360) lastAngle -= 360;
      if (lastAngle < 0) lastAngle += 360;
    } else {
      // If we hit the boundary, force lastAngle to align with the handle
      // so if they move away and come back, it doesn't desync wildly
      const ozMod = currentOz.value % fluidLimit.value;
      lastAngle = ozMod * (360 / fluidLimit.value);
    }
  }
};

const handlePointerUp = () => {
  isDragging.value = false;
  window.removeEventListener('pointermove', handlePointerMove);
  window.removeEventListener('pointerup', handlePointerUp);
};

onUnmounted(() => {
  window.removeEventListener('pointermove', handlePointerMove);
  window.removeEventListener('pointerup', handlePointerUp);
});

const handleAngleFromClick = (e) => {
  if (isDragging.value) return; // handled by pointerdown
  const rect = sliderRef.value.getBoundingClientRect();
  const x = ((e.clientX - rect.left) / rect.width) * 300;
  const y = ((e.clientY - rect.top) / rect.height) * 300;
  lastAngle = getAngle(x, y);
  // Just set the angle as the starting point for dragging
};

const emit = defineEmits(['logged']);

const submitIntake = async () => {
  if (currentOz.value === 0) {
    showAlert("Please enter an amount greater than 0.", "error");
    return;
  }
  
  isSubmitting.value = true;
  try {
    const volumeMl = Math.round(currentOz.value * 29.5735);
    await api.intake.post("/intake/manual", {
      user_id: userProfile.value?.uid || "default_user",
      volume_ml: volumeMl
    });
    emit('logged', `Successfully logged ${displayValue.value} ${displayUnit.value}!`);
    currentOz.value = 0;
  } catch (error) {
    console.error("Error logging intake:", error);
    showAlert("Failed to log intake.", "error");
  } finally {
    isSubmitting.value = false;
  }
};

// Calculate handle position based on currentOz (modulo fluidLimit)
const handlePos = computed(() => {
  const ozMod = currentOz.value % fluidLimit.value;
  const angleRad = (ozMod * (360 / fluidLimit.value)) * (Math.PI / 180);
  return {
    x: center.x + radius * Math.cos(angleRad),
    y: center.y + radius * Math.sin(angleRad)
  };
});

const buttonText = computed(() => {
  if (isSubmitting.value) return 'Logging...';
  return resetMode.value === 'daily' ? 'Log for the Day' : 'Log for the Period';
});

const measurementSystem = inject('measurementSystem');
const displayValue = computed(() => {
  return measurementSystem.value === 'ml' ? Math.round(currentOz.value * 29.5735) : currentOz.value;
});
const displayUnit = computed(() => measurementSystem.value === 'ml' ? 'mL' : 'oz');
</script>

<template>
  <div class="enter-layout">
    <section class="enter-page">
      <h1>Track Your Fluid</h1>
      
      <div class="interactive-area">
        <div class="cup-section">
          <div class="cup-grid">
            <button 
              v-for="i in 8" 
              :key="i"
              class="small-cup-btn"
              :title="measurementSystem === 'ml' ? '240 mL Cup' : '8 oz Cup'"
              @click="setCupLevel(i)"
              :aria-label="measurementSystem === 'ml' ? `Set ${i * 240} mL` : `Set ${i * 8} oz`"
            >
              <svg width="32" height="32" viewBox="0 0 24 24" :fill="i <= Math.floor(currentOz / 8) ? '#007BFF' : 'none'" stroke="#007BFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 8h1a4 4 0 1 1 0 8h-1"></path>
                <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"></path>
              </svg>
            </button>
          </div>
        </div>

        <div class="slider-section">
          <div class="slider-container" ref="sliderRef" 
               @pointerdown="handlePointerDown"
               :title="measurementSystem === 'ml' ? 'Slide around the circle to add/remove by 30 mL' : 'Slide around the circle to add/remove by 1 oz'"
               style="touch-action: none;">
            <svg width="180" height="180" viewBox="0 0 300 300">
            <defs>
              <clipPath id="cup-clip">
                <rect x="90" :y="200 - (currentOz / fluidLimit) * 100" width="120" :height="(currentOz / fluidLimit) * 100" />
              </clipPath>
            </defs>
            <circle cx="150" cy="150" r="120" fill="none" stroke="#C0C0C0" stroke-width="20" class="slider-track" />
            
            <circle 
              :cx="handlePos.x" 
              :cy="handlePos.y" 
              r="20" 
              fill="#007BFF" 
              class="handle"
            />
            
            <!-- Filled region of the cup -->
            <path 
              d="M 110,100 L 120,195 A 5,5 0 0,0 125,200 L 175,200 A 5,5 0 0,0 180,195 L 190,100 Z" 
              fill="#00CFFF" 
              clip-path="url(#cup-clip)"
            />

            <!-- Cup Outline -->
            <path 
              d="M 110,100 L 120,195 A 5,5 0 0,0 125,200 L 175,200 A 5,5 0 0,0 180,195 L 190,100" 
              fill="none" 
              stroke="#007BFF" 
              stroke-width="4" 
              stroke-linecap="round"
            />
            
            <text x="150" y="150" text-anchor="middle" dominant-baseline="middle" class="oz-display">
              {{ displayValue }} {{ displayUnit }}
            </text>
          </svg>
        </div>

        <div class="slider-actions">
          <button class="scan-btn" @click="() => showAlert('AI Scan functionality coming soon!')" title="Scan with AI">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z" />
              <circle cx="12" cy="13" r="4" />
            </svg>
            <span>AI Scan</span>
          </button>

          <!-- Barcode Scan Button -->
          <button class="scan-btn barcode-btn" @click="isScannerOpen = true" title="Scan Barcode">
            <svg width="20" height="20" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M3 4a1 1 0 011-1h4a1 1 0 010 2H5v3a1 1 0 01-2 0V4zm0 16a1 1 0 001 1h4a1 1 0 000-2H5v-3a1 1 0 00-2 0v4zm17-16a1 1 0 00-1-1h-4a1 1 0 000 2h3v3a1 1 0 002 0V4zm0 16a1 1 0 01-1 1h-4a1 1 0 010-2h3v-3a1 1 0 012 0v4z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M7 8v8M10 8v8M14 8v8M17 8v8" />
            </svg>
            <span>{{ isLookingUp ? 'Searching...' : 'Barcode' }}</span>
          </button>
        </div>
      </div>
      </div>
      
      <!-- Scanner Modal -->
      <BarcodeScanner v-if="isScannerOpen" @close="isScannerOpen = false" @scan="handleBarcodeScan" />
    </section>
    
    <div class="submit-section">
      <button class="submit-btn" @click="submitIntake" :disabled="isSubmitting">
        {{ buttonText }}
      </button>
    </div>
  </div>
</template>

<style scoped>
.enter-layout {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.enter-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.1);
  max-width: 500px;
  width: 100%;
  margin: 0 auto;
  margin-bottom: auto;
}

.user-greeting {
  font-size: 1.125rem;
  font-weight: 600;
  color: #3b82f6;
  margin: 0;
  margin-bottom: 0.25rem;
  text-align: center;
  font-style: italic;
}

h1 {
  color: #007BFF;
  margin-top: 0;
  margin-bottom: 24px;
}

.interactive-area {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 24px;
  width: 100%;
  margin-bottom: 16px;
}

.cup-section {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.section-title {
  color: #666666;
  font-size: 0.9rem;
  font-weight: 600;
  text-align: center;
  margin-bottom: 12px;
  margin-top: 0;
}

.cup-grid {
  display: grid;
  grid-template-columns: repeat(4, auto);
  gap: 12px 16px;
  justify-content: center;
}

.small-cup-btn {
  background: transparent;
  border: none;
  padding: 4px;
  cursor: pointer;
  transition: transform 0.2s;
}

.small-cup-btn:hover {
  transform: translateY(-2px);
}

.slider-section {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.slider-container {
  cursor: grab;
}

.slider-container:active {
  cursor: grabbing;
}

.handle {
  transition: cx 0.1s, cy 0.1s;
  cursor: grab;
}

.oz-display {
  font-size: 23.41px;
  font-weight: bold;
  fill: #007BFF;
  text-shadow: 0 0 4px white, 0 0 8px white;
}

.slider-actions {
  width: 100%;
  display: flex;
  flex-direction: row;
  align-items: center;
  justify-content: center;
  gap: 16px;
  margin-top: 8px;
  margin-bottom: 4px;
  padding-left: 0;
}

.scan-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  border: 1px solid #C0C0C0;
  color: #333333;
  padding: 6px 12px;
  border-radius: 9999px;
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
  box-shadow: 0 1px 2px rgba(0,0,0,0.05);
}

.scan-btn:hover {
  background: #e2e8f0;
  color: #0A0A0A;
  border-color: #C0C0C0;
}

.instruction {
  color: #666666;
  font-size: 0.8rem;
  font-style: italic;
  text-align: center;
  margin-top: 8px;
}

.submit-section {
  width: 100%;
  position: sticky;
  bottom: 0;
  background: white;
  padding: 10px;
  z-index: 10;
  margin-top: auto;
}

.submit-btn {
  width: 100%;
  padding: 10px;
  background: #C0C0C0;
  color: #0A0A0A;
  border: none;
  border-radius: 50px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #A0A0A0;
}

.submit-btn:disabled {
  background: #C0C0C0;
  cursor: not-allowed;
}
</style>
