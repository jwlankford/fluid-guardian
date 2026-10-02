<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import api from '../services/api.js';

const currentOz = ref(0);
const isSubmitting = ref(false);

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
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  lastAngle = getAngle(x, y);
  
  // Also add global event listeners for drag and up
  window.addEventListener('pointermove', handlePointerMove);
  window.addEventListener('pointerup', handlePointerUp);
};

const handlePointerMove = (e) => {
  if (!isDragging.value || !sliderRef.value) return;
  const rect = sliderRef.value.getBoundingClientRect();
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
  
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
  const x = e.clientX - rect.left;
  const y = e.clientY - rect.top;
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
        <svg width="300" height="300" viewBox="0 0 300 300">
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
      <p class="instruction">Slide around the circle to add/remove by 1 oz</p>
    </div>

    <div class="submit-section">
      <button class="submit-btn" @click="submitIntake" :disabled="isSubmitting">
        {{ isSubmitting ? 'Logging...' : 'Log for the Day' }}
      </button>
    </div>
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

h1 {
  color: #0369a1;
  margin-bottom: 24px;
}

.cup-section {
  margin-bottom: 32px;
}

.cup-grid {
  display: flex;
  gap: 8px;
  justify-content: center;
  flex-wrap: wrap;
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
  margin-bottom: 32px;
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
  font-size: 36px;
  font-weight: bold;
  fill: #0369a1;
  text-shadow: 0 0 4px white, 0 0 8px white;
}

.instruction {
  color: #64748b;
  font-size: 0.9rem;
  margin-top: 16px;
}

.submit-section {
  width: 100%;
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
