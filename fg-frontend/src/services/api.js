import axios from "axios";

const services = {
  intake: import.meta.env.VITE_INTAKE_API_URL ?? "http://localhost:8001",
  prediction: import.meta.env.VITE_PREDICTION_API_URL ?? "http://localhost:8002",
  safety: import.meta.env.VITE_SAFETY_API_URL ?? "http://localhost:8003",
  reporting: import.meta.env.VITE_REPORTING_API_URL ?? "http://localhost:8004",
  learning: import.meta.env.VITE_LEARNING_API_URL ?? "http://localhost:8005",
  nutrition: import.meta.env.VITE_NUTRITION_API_URL ?? "http://localhost:8006",
  intervention: import.meta.env.VITE_INTERVENTION_API_URL ?? "http://localhost:8007",
};

export const api = Object.fromEntries(
  Object.entries(services).map(([name, baseURL]) => [
    name,
    axios.create({ baseURL, headers: { "Content-Type": "application/json" } }),
  ]),
);

export default api;
