<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../services/api.js';
import { useAuth } from '../composables/useAuth.js';
import BarcodeScanner from '../components/BarcodeScanner.vue';

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
        const ozMod = currentOz.value % 64;
        lastAngle = ozMod * (360 / 64);
        alert(`Found ${data.product.product_name || 'Product'}!\nLoaded ${oz} oz.`);
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
  const ozMod = currentOz.value % 64;
  lastAngle = ozMod * (360 / 64);
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
  
  // 360 degrees = 64 ounces (5.625 degrees per oz)
  const degreesPerOz = 360 / 64;
  
  if (Math.abs(diff) >= degreesPerOz) {
    const ticks = Math.floor(Math.abs(diff) / degreesPerOz) * Math.sign(diff);
    const newOz = Math.max(0, Math.min(64, currentOz.value + ticks));
    
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
      const ozMod = currentOz.value % 64;
      lastAngle = ozMod * (360 / 64);
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

const submitIntake = async () => {
  if (currentOz.value === 0) {
    alert("Please enter an amount greater than 0.");
    return;
  }
  
  isSubmitting.value = true;
  try {
    const volumeMl = Math.round(currentOz.value * 29.5735);
    await api.intake.post("/intake/manual", {
      user_id: "default_user",
      volume_ml: volumeMl
    });
    alert(`Successfully logged ${currentOz.value} oz (${volumeMl} ml)!`);
    currentOz.value = 0;
  } catch (error) {
    console.error("Error logging intake:", error);
    alert("Failed to log intake.");
  } finally {
    isSubmitting.value = false;
  }
};

// Calculate handle position based on currentOz (modulo 64)
const handlePos = computed(() => {
  const ozMod = currentOz.value % 64;
  const angleRad = (ozMod * (360 / 64)) * (Math.PI / 180);
  return {
    x: center.x + radius * Math.cos(angleRad),
    y: center.y + radius * Math.sin(angleRad)
  };
});
</script>

<template>
  <section class="enter-page">
    <h2 v-if="isLoggedIn && userProfile" class="user-greeting">Hi, {{ userProfile.firstName }}</h2>
    <h1>Log Fluid Intake</h1>
    
    <div class="cup-section">
      <div class="cup-grid">
        <button 
          v-for="i in 8" 
          :key="i"
          class="small-cup-btn"
          @click="setCupLevel(i)"
          :aria-label="`Set ${i * 8} oz`"
        >
          <svg width="32" height="32" viewBox="0 0 24 24" :fill="i <= Math.floor(currentOz / 8) ? '#0284c7' : 'none'" stroke="#0284c7" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
            <path d="M17 8h1a4 4 0 1 1 0 8h-1"></path>
            <path d="M3 8h14v9a4 4 0 0 1-4 4H7a4 4 0 0 1-4-4Z"></path>
          </svg>
        </button>
      </div>
    </div>

    <div class="slider-section">
      <div class="slider-container" ref="sliderRef" 
           @pointerdown="handlePointerDown"
           style="touch-action: none;">
        <svg width="240" height="240" viewBox="0 0 300 300">
          <defs>
            <clipPath id="cup-clip">
              <rect x="90" :y="200 - (currentOz / 64) * 100" width="120" :height="(currentOz / 64) * 100" />
            </clipPath>
          </defs>
          
          <circle cx="150" cy="150" r="120" fill="none" stroke="#bae6fd" stroke-width="20" />
          
          <circle 
            :cx="handlePos.x" 
            :cy="handlePos.y" 
            r="20" 
            fill="#0284c7" 
            class="handle"
          />
          
          <!-- Filled region of the cup -->
          <path 
            d="M 110,100 L 120,195 A 5,5 0 0,0 125,200 L 175,200 A 5,5 0 0,0 180,195 L 190,100 Z" 
            fill="#38bdf8" 
            clip-path="url(#cup-clip)"
          />

          <!-- Cup Outline -->
          <path 
            d="M 110,100 L 120,195 A 5,5 0 0,0 125,200 L 175,200 A 5,5 0 0,0 180,195 L 190,100" 
            fill="none" 
            stroke="#0284c7" 
            stroke-width="4" 
            stroke-linecap="round"
          />
          
          <text x="150" y="150" text-anchor="middle" dominant-baseline="middle" class="oz-display">
            {{ currentOz }} oz
          </text>
        </svg>
      </div>
      
      <div class="slider-actions">
        <!-- AI Scan Button (Future) -->
        <button class="scan-btn" @click="() => alert('AI Scan functionality coming soon!')" title="Scan with AI">
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

      <p class="instruction">Slide around the circle to add/remove by 1 oz</p>
    </div>

    <div class="submit-section">
      <button class="submit-btn" @click="submitIntake" :disabled="isSubmitting">
        {{ isSubmitting ? 'Logging...' : 'Log for the Day' }}
      </button>
    </div>

    <!-- Scanner Modal -->
    <BarcodeScanner v-if="isScannerOpen" @close="isScannerOpen = false" @scan="handleBarcodeScan" />
  </section>
</template>

<style scoped>
.enter-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 20px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.1);
  max-width: 500px;
  margin: 0 auto;
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
  color: #0369a1;
  margin-top: 0;
  margin-bottom: 24px;
}

.cup-section {
  margin-bottom: 16px;
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
  margin-bottom: 16px;
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
  fill: #0369a1;
  text-shadow: 0 0 4px white, 0 0 8px white;
}

.slider-actions {
  width: 100%;
  display: flex;
  justify-content: flex-start;
  gap: 12px;
  margin-top: 8px;
  margin-bottom: 4px;
  padding-left: 12px;
}

.scan-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: #f1f5f9;
  border: 1px solid #cbd5e1;
  color: #334155;
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
  color: #0f172a;
  border-color: #94a3b8;
}

.instruction {
  color: #64748b;
  font-size: 0.9rem;
  margin-top: 8px;
}

.submit-section {
  width: 100%;
  position: sticky;
  bottom: 0;
  background: white;
  padding: 16px 0;
  z-index: 10;
  margin-top: auto;
}

.submit-btn {
  width: 100%;
  padding: 16px;
  background: #0284c7;
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1.2rem;
  font-weight: bold;
  cursor: pointer;
  transition: background 0.2s;
}

.submit-btn:hover:not(:disabled) {
  background: #0369a1;
}

.submit-btn:disabled {
  background: #94a3b8;
  cursor: not-allowed;
}
</style>
