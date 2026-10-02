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
}

h2,
p {
  margin: 0 0 8px;
}

p {
  text-transform: capitalize;
}
</style>
