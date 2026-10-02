<script setup>
import { ref, onBeforeUnmount } from 'vue';
import { api } from '../services/api';

const uploadStatus = ref('');
const result = ref(null);

const isCameraActive = ref(false);
const videoRef = ref(null);
const canvasRef = ref(null);

const uploadBase64 = async (base64) => {
  try {
    uploadStatus.value = 'Uploading...';
    result.value = null;
    const response = await api.intake.post('/intake/image', {
      user_id: 'user_123', // hardcoded for now or get from auth context
      image_reference: base64
    });
    
    result.value = response.data;
    uploadStatus.value = 'Upload successful!';
  } catch (err) {
    console.error('API Error:', err);
    uploadStatus.value = 'Upload failed.';
  }
};

const handleFileUpload = async (event) => {
  const file = event.target.files[0];
  if (!file) return;

  const reader = new FileReader();
  reader.onload = (e) => {
    uploadBase64(e.target.result);
  };
  reader.onerror = () => {
    uploadStatus.value = 'File read failed.';
  };
  reader.readAsDataURL(file);
};

const startCamera = async () => {
  try {
    uploadStatus.value = '';
    result.value = null;
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } 
    });
    isCameraActive.value = true;
    
    // We need to wait for the DOM to update so videoRef is available
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
  isCameraActive.value = false;
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

// Cleanup on component unmount
onBeforeUnmount(() => {
  stopCamera();
});
</script>

<template>
  <section class="card" aria-label="Upload item">
    <h2>Upload Item</h2>
    <p>Take a photo or upload an image of your food or drink.</p>
    
    <div v-if="!isCameraActive" class="upload-controls">
      <div class="actions">
        <button type="button" @click="startCamera" class="action-btn">
          Take Photo
        </button>
        <span class="or">or</span>
        <label class="action-btn secondary">
          Upload File
          <input 
            type="file" 
            @change="handleFileUpload" 
            accept="image/*" 
            class="hidden-input"
          />
        </label>
      </div>
    </div>

    <div v-else class="camera-container">
      <video ref="videoRef" class="camera-video" playsinline></video>
      <canvas ref="canvasRef" style="display: none;"></canvas>
      <div class="camera-actions">
        <button type="button" @click="capturePhoto" class="action-btn">Snap Photo</button>
        <button type="button" @click="stopCamera" class="action-btn secondary">Cancel</button>
      </div>
    </div>

    <p v-if="uploadStatus" class="status">{{ uploadStatus }}</p>
    
    <div v-if="result" class="result">
      <p><strong>Result:</strong></p>
      <pre>{{ JSON.stringify(result, null, 2) }}</pre>
    </div>
  </section>
</template>

<style scoped>
.card {
  padding: 20px;
  border-radius: 10px;
  background: white;
  box-shadow: 0 1px 4px rgba(2, 132, 199, 0.1);
  border-top: 4px solid #00CFFF;
}

h2 {
  color: #007BFF;
  margin: 0 0 8px;
}

p {
  margin: 0 0 8px;
}

.upload-controls {
  margin: 16px 0;
}

.actions, .camera-actions {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.camera-container {
  margin: 16px 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.camera-video {
  width: 100%;
  max-width: 400px;
  border-radius: 8px;
  background: #000;
  border: 2px solid #007BFF;
}

.action-btn {
  display: inline-block;
  padding: 8px 16px;
  background: #007BFF;
  color: white;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  font-weight: 600;
  font-size: 1rem;
  text-align: center;
  transition: background 0.2s;
}

.action-btn:hover {
  background: #007BFF;
}

.action-btn.secondary {
  background: #F8F9FA;
  color: #007BFF;
}

.action-btn.secondary:hover {
  background: #C0C0C0;
}

.hidden-input {
  display: none;
}

.or {
  font-size: 0.9rem;
  color: #6b7280;
}

.status {
  color: #007BFF;
  font-weight: 500;
  margin-top: 12px;
}

.result {
  margin-top: 16px;
  padding: 12px;
  background: #F8F9FA;
  border-radius: 6px;
  overflow-x: auto;
  border: 1px solid #C0C0C0;
}

pre {
  margin: 0;
  font-size: 0.85rem;
  color: #0c4a6e;
}
</style>
