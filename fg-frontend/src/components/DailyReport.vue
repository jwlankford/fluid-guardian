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
  box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.1), 0 2px 4px -1px rgba(2, 132, 199, 0.06);
  border-top: 4px solid #00CFFF;
}

h2,
p {
  margin: 0 0 8px;
}

h2 {
  color: #007BFF;
}
</style>
