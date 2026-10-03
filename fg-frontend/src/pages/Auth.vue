<script setup>
import { ref } from 'vue';
import { useAuth } from '../composables/useAuth';

const { loginWithEmail, registerWithEmail, login } = useAuth();

const isRegistering = ref(false);
const email = ref('');
const password = ref('');
const errorMsg = ref('');
const loading = ref(false);

const handleSubmit = async () => {
  errorMsg.value = '';
  loading.value = true;
  try {
    if (isRegistering.value) {
      await registerWithEmail(email.value, password.value);
    } else {
      await loginWithEmail(email.value, password.value);
    }
  } catch (err) {
    errorMsg.value = err.message || 'Authentication failed';
  } finally {
    loading.value = false;
  }
};

const handleGoogleLogin = async () => {
  errorMsg.value = '';
  try {
    await login();
  } catch (err) {
    errorMsg.value = err.message || 'Google Auth failed';
  }
};
</script>

<template>
  <div class="auth-wrapper">
    <div class="auth-card">
      <img src="../assets/images/logo-full.png" alt="Fluid Guardian Logo" class="auth-logo" />
      <p class="auth-subtitle">{{ isRegistering ? 'Create an account' : 'Sign in to your account' }}</p>

      <form @submit.prevent="handleSubmit" class="auth-form">
        <div class="input-group">
          <label>Email</label>
          <input type="email" v-model="email" required placeholder="name@example.com" />
        </div>
        
        <div class="input-group">
          <label>Password</label>
          <input type="password" v-model="password" required placeholder="••••••••" />
        </div>

        <p v-if="errorMsg" class="error-msg">{{ errorMsg }}</p>

        <button type="submit" class="primary-btn" :disabled="loading">
          {{ loading ? 'Please wait...' : (isRegistering ? 'Sign Up' : 'Sign In') }}
        </button>
      </form>

      <div class="divider">
        <span>or</span>
      </div>

      <button @click="handleGoogleLogin" type="button" class="google-btn">
        <svg viewBox="0 0 24 24" width="20" height="20" xmlns="http://www.w3.org/2000/svg"><path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/><path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.16v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/><path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.16C1.43 8.55 1 10.22 1 12s.43 3.45 1.16 4.93l3.68-2.84z" fill="#FBBC05"/><path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.16 7.07l3.68 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/></svg>
        Continue with Google
      </button>

      <p class="toggle-mode">
        {{ isRegistering ? 'Already have an account?' : 'Need an account?' }}
        <button type="button" @click="isRegistering = !isRegistering" class="link-btn">
          {{ isRegistering ? 'Sign In' : 'Sign Up' }}
        </button>
      </p>
    </div>
  </div>
</template>

<style scoped>
.auth-wrapper {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  width: 100%;
  padding: 20px;
  background: #F8F9FA;
  overflow-y: auto;
}

.auth-card {
  background: white;
  padding: 32px;
  border-radius: 16px;
  box-shadow: 0 10px 25px rgba(0,0,0,0.1);
  width: 100%;
  max-width: 400px;
  text-align: center;
}

.auth-logo {
  height: 64px;
  width: auto;
  object-fit: contain;
  margin-bottom: 16px;
}

.auth-subtitle {
  color: #666666;
  margin: 0 0 24px;
}

.auth-form {
  display: flex;
  flex-direction: column;
  gap: 16px;
  text-align: left;
}

.input-group label {
  display: block;
  font-size: 0.875rem;
  font-weight: 600;
  color: #333333;
  margin-bottom: 6px;
}

.input-group input {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #C0C0C0;
  border-radius: 8px;
  font-size: 1rem;
  outline: none;
  transition: border-color 0.2s;
}

.input-group input:focus {
  border-color: #007BFF;
  box-shadow: 0 0 0 3px rgba(2, 132, 199, 0.1);
}

.error-msg {
  color: #ef4444;
  font-size: 0.875rem;
  margin: 0;
  text-align: center;
}

.primary-btn {
  background: #007BFF;
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.primary-btn:hover:not(:disabled) {
  background: #007BFF;
}

.primary-btn:disabled {
  background: #C0C0C0;
  cursor: not-allowed;
}

.divider {
  display: flex;
  align-items: center;
  margin: 24px 0;
  color: #C0C0C0;
  font-size: 0.875rem;
}

.divider::before, .divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: #e2e8f0;
}

.divider span {
  padding: 0 10px;
}

.google-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 10px;
  background: white;
  border: 1px solid #C0C0C0;
  color: #333333;
  border-radius: 8px;
  padding: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.2s;
}

.google-btn:hover {
  background: #f8fafc;
}

.toggle-mode {
  margin-top: 24px;
  font-size: 0.875rem;
  color: #666666;
}

.link-btn {
  background: none;
  border: none;
  color: #007BFF;
  font-weight: 600;
  cursor: pointer;
  padding: 0;
}

.link-btn:hover {
  text-decoration: underline;
}
</style>
