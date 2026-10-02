import { ref } from 'vue';
import { onAuthStateChanged } from 'firebase/auth';
import { auth, googleProvider, signInWithPopup, signOut as firebaseSignOut } from '../services/firebase.js';

const isLoggedIn = ref(false);
const userProfile = ref(null);

// Listen for auth state changes immediately
onAuthStateChanged(auth, (user) => {
  if (user) {
    userProfile.value = {
      name: user.displayName,
      email: user.email,
      picture: user.photoURL,
      firstName: user.displayName?.split(' ')[0] || 'User'
    };
    isLoggedIn.value = true;
  } else {
    userProfile.value = null;
    isLoggedIn.value = false;
  }
});

export function useAuth() {
  const login = async () => {
    try {
      await signInWithPopup(auth, googleProvider);
    } catch (error) {
      console.error("Firebase Login Error:", error);
    }
  };

  const logout = async () => {
    try {
      await firebaseSignOut(auth);
    } catch (error) {
      console.error("Firebase Logout Error:", error);
    }
  };

  return {
    isLoggedIn,
    userProfile,
    login,
    logout
  };
}
