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
  box-shadow: 0 1px 4px #1f29371a;
}

h2,
p {
  margin: 0 0 8px;
}

.amount {
  color: #14566b;
  font-size: 1.75rem;
  font-weight: 700;
}
</style>
