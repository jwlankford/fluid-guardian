<script setup>
import { ref, onBeforeUnmount } from "vue";
import Dashboard from "./pages/Dashboard.vue";
import Reports from "./pages/Reports.vue";
import api from "./services/api.js";

const currentPage = ref("dashboard");
const isNavMenuOpen = ref(false);
const isAddMenuOpen = ref(false);

const fileInput = ref(null);

const toggleNavMenu = () => {
  isNavMenuOpen.value = !isNavMenuOpen.value;
  if (isNavMenuOpen.value) isAddMenuOpen.value = false;
};

const toggleAddMenu = () => {
  isAddMenuOpen.value = !isAddMenuOpen.value;
  if (isAddMenuOpen.value) isNavMenuOpen.value = false;
};

const navigateTo = (page) => {
  currentPage.value = page;
  isNavMenuOpen.value = false;
};

// Camera Modal Logic
const isCameraModalOpen = ref(false);
const videoRef = ref(null);
const canvasRef = ref(null);
const uploadStatus = ref("");

const triggerCamera = async () => {
  isAddMenuOpen.value = false;
  isCameraModalOpen.value = true;
  uploadStatus.value = "";
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } 
    });
    setTimeout(() => {
      if (videoRef.value) {
        videoRef.value.srcObject = stream;
        videoRef.value.play();
      }
    }, 50);
  } catch (err) {
    console.error("Camera access error:", err);
    uploadStatus.value = "Camera access denied or unavailable.";
  }
};

const stopCamera = () => {
  if (videoRef.value && videoRef.value.srcObject) {
    videoRef.value.srcObject.getTracks().forEach(track => track.stop());
    videoRef.value.srcObject = null;
  }
  isCameraModalOpen.value = false;
};

const capturePhoto = () => {
  if (videoRef.value && canvasRef.value) {
    const video = videoRef.value;
    const canvas = canvasRef.value;
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const base64 = canvas.toDataURL('image/jpeg');
    stopCamera();
    uploadBase64(base64);
  }
};

const triggerUpload = () => {
  isAddMenuOpen.value = false;
  fileInput.value.click();
};

const uploadBase64 = async (base64) => {
  try {
    uploadStatus.value = "Uploading...";
    await api.intake.post("/intake/image", {
      user_id: "default_user",
      image_reference: base64,
    });
    alert("Image uploaded successfully!");
    uploadStatus.value = "";
  } catch (error) {
    console.error("Error uploading image:", error);
    alert("Failed to upload image.");
    uploadStatus.value = "";
  }
};

const handleImageUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = async (e) => {
    uploadBase64(e.target.result);
  };
  reader.readAsDataURL(file);
  event.target.value = ''; // Reset input
};

onBeforeUnmount(() => {
  stopCamera();
});
</script>

<template>
  <main class="app-shell">
    <header class="app-header">
      <a class="brand" href="#" @click.prevent="navigateTo('dashboard')">
        Fluid Guardian
      </a>
      
      <div class="header-actions">
        <!-- Add Menu -->
        <div class="menu-container">
          <button class="icon-button" @click="toggleAddMenu" aria-label="Add options">
            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M12 4v16m8-8H4" />
            </svg>
          </button>
          <div v-if="isAddMenuOpen" class="dropdown-menu">
            <button @click="triggerCamera">Take Photo</button>
            <button @click="triggerUpload">Upload Photo</button>
          </div>

          <!-- Hidden input for file selection -->
          <input type="file" ref="fileInput" accept="image/*" style="display: none" @change="handleImageUpload" />
        </div>

        <!-- Hamburger Nav Menu -->
        <div class="menu-container">
          <button class="icon-button" @click="toggleNavMenu" aria-label="Main navigation">
            <svg width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          </button>
          <nav v-if="isNavMenuOpen" class="dropdown-menu" aria-label="Main navigation">
            <button
              :aria-current="currentPage === 'dashboard' ? 'page' : undefined"
              @click="navigateTo('dashboard')"
            >
              Dashboard
            </button>
            <button
              :aria-current="currentPage === 'reports' ? 'page' : undefined"
              @click="navigateTo('reports')"
            >
              Reports
            </button>
          </nav>
        </div>
      </div>
    </header>

    <Dashboard v-if="currentPage === 'dashboard'" />
    <Reports v-else />

    <!-- Camera Modal Overlay -->
    <div v-if="isCameraModalOpen" class="camera-modal">
      <div class="camera-modal-content">
        <h3>Take Photo</h3>
        <video ref="videoRef" class="camera-video" playsinline></video>
        <canvas ref="canvasRef" style="display: none;"></canvas>
        <p v-if="uploadStatus" class="status">{{ uploadStatus }}</p>
        <div class="camera-actions">
          <button type="button" @click="capturePhoto" class="action-btn">Snap Photo</button>
          <button type="button" @click="stopCamera" class="action-btn secondary">Cancel</button>
        </div>
      </div>
    </div>
  </main>
</template>

<style>
:root {
  font-family: Arial, sans-serif;
  color: #1f2937;
  background: #e0f2fe; /* Light blue background */
  font-synthesis: none;
  text-rendering: optimizeLegibility;
}

body {
  min-width: 320px;
  margin: 0;
}

button {
  font: inherit;
  cursor: pointer;
}

.app-shell {
  max-width: 960px;
  margin: 0 auto;
  padding: 24px;
}

.app-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 32px;
  background-color: #0369a1; /* Blue header */
  padding: 16px 24px;
  border-radius: 12px;
  color: #ffffff;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.brand {
  color: inherit;
  font-size: 1.5rem;
  font-weight: 700;
  text-decoration: none;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.menu-container {
  position: relative;
}

.app-header button {
  padding: 8px 16px;
  border: 0;
  border-radius: 6px;
  background: transparent;
  color: #bae6fd; /* Light blue text for inactive buttons */
  transition: all 0.2s ease;
}

.app-header button:hover {
  background: rgba(255, 255, 255, 0.1);
  color: #ffffff;
}

.app-header button.icon-button {
  padding: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
}

.app-header .dropdown-menu {
  position: absolute;
  top: 100%;
  right: 0;
  margin-top: 8px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
  padding: 8px;
  display: flex;
  flex-direction: column;
  min-width: 160px;
  z-index: 10;
  border: 1px solid #e5e7eb;
}

.app-header .dropdown-menu button {
  width: 100%;
  text-align: left;
  padding: 10px 16px;
  color: #374151; /* Dark text for dropdown */
  background: transparent;
  border-radius: 6px;
}

.app-header .dropdown-menu button:hover {
  background: #f3f4f6;
  color: #0369a1;
}

.app-header .dropdown-menu button[aria-current="page"] {
  background: #e0f2fe;
  color: #0369a1;
  font-weight: bold;
}

/* Camera Modal Styles */
.camera-modal {
  position: fixed;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}
.camera-modal-content {
  background: white;
  padding: 24px;
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  gap: 16px;
  max-width: 90vw;
  width: 450px;
}
.camera-modal-content h3 {
  margin: 0;
  color: #0369a1;
}
.camera-video {
  width: 100%;
  border-radius: 8px;
  background: #000;
  border: 2px solid #0284c7;
}
.camera-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}
.action-btn {
  padding: 8px 16px;
  background: #0284c7;
  color: white;
  border: none;
  border-radius: 6px;
  font-weight: 600;
  cursor: pointer;
}
.action-btn:hover {
  background: #0369a1;
}
.action-btn.secondary {
  background: #e0f2fe;
  color: #0284c7;
}
.action-btn.secondary:hover {
  background: #bae6fd;
}
.status {
  color: #0369a1;
  font-weight: 500;
  margin: 0;
}
</style>
