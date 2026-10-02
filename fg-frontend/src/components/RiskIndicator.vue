<script setup>
defineProps({
  level: {
    type: String,
    default: "unknown",
  },
});
</script>

<template>
  <section class="indicator" aria-live="polite">
    <h2>Risk level</h2>
    <p>{{ level }}</p>
  </section>
</template>

<style scoped>
.indicator {
  padding: 20px;
  border-radius: 10px;
  background: white;
  box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.1), 0 2px 4px -1px rgba(2, 132, 199, 0.06);
  border-top: 4px solid #7dd3fc;
}

h2,
p {
  margin: 0 0 8px;
}

h2 {
  color: #0369a1;
}

p {
  text-transform: capitalize;
}
</style>
