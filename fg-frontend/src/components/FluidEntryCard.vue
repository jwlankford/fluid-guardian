<script setup>
defineProps({
  amountMl: {
    type: Number,
    default: 0,
  },
  description: {
    type: String,
    default: "Today's recorded fluid intake",
  },
});
</script>

<template>
  <section class="card" aria-label="Fluid intake">
    <h2>Fluid intake</h2>
    <p class="amount">{{ amountMl }} ml</p>
    <p>{{ description }}</p>
  </section>
</template>

<style scoped>
.card {
  padding: 20px;
  border-radius: 10px;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.1), 0 2px 4px -1px rgba(2, 132, 199, 0.06);
  border-top: 4px solid #38bdf8;
}

h2,
p {
  margin: 0 0 8px;
}

h2 {
  color: #0369a1;
}

.amount {
  color: #0284c7;
  font-size: 1.75rem;
  font-weight: 700;
}
</style>
