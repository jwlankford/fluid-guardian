import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut } from 'firebase/auth';
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyDwX-XHo4DNb0Jgz-e89atyMyGcwk5dt1E",
  authDomain: "fluid-guardian.firebaseapp.com",
  projectId: "fluid-guardian",
  storageBucket: "fluid-guardian.firebasestorage.app",
  messagingSenderId: "113680969985",
  appId: "1:113680969985:web:9fd61c0ed603106f636b00",
  measurementId: "G-JVNPLYQM60"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const auth = getAuth(app);
const analytics = getAnalytics(app);
const googleProvider = new GoogleAuthProvider();

export { auth, auth as authService, googleProvider, signInWithPopup, signOut };
