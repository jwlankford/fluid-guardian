<script setup>
defineProps({
  summary: {
    type: String,
    default: "Your daily summary will appear here.",
  },
});
</script>

<template>
  <section class="report">
    <h2>Daily report</h2>
    <p>{{ summary }}</p>
  </section>
</template>

<style scoped>
.report {
  padding: 20px;
  border-radius: 10px;
  background: white;
}

h2,
p {
  margin: 0 0 8px;
}
</style>
