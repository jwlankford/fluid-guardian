import { ref } from 'vue';
import { onAuthStateChanged, createUserWithEmailAndPassword, signInWithEmailAndPassword } from 'firebase/auth';
import { auth, googleProvider, signInWithPopup, signOut as firebaseSignOut } from '../services/firebase.js';

const isLoggedIn = ref(false);
const userProfile = ref(null);

// Listen for auth state changes immediately
onAuthStateChanged(auth, (user) => {
  if (user) {
    userProfile.value = {
      uid: user.uid,
      name: user.displayName || user.email?.split('@')[0],
      email: user.email,
      picture: user.photoURL,
      firstName: (user.displayName || user.email?.split('@')[0])?.split(' ')[0] || 'User'
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
      throw error;
    }
  };

  const loginWithEmail = async (email, password) => {
    try {
      await signInWithEmailAndPassword(auth, email, password);
    } catch (error) {
      console.error("Firebase Email Login Error:", error);
      throw error;
    }
  };

  const registerWithEmail = async (email, password) => {
    try {
      await createUserWithEmailAndPassword(auth, email, password);
    } catch (error) {
      console.error("Firebase Registration Error:", error);
      throw error;
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
    loginWithEmail,
    registerWithEmail,
    logout
  };
}
