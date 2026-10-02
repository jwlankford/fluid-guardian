with open('src/pages/Dashboard.vue', 'r', encoding='utf-8') as f:
    content = f.read()

if 'const isDaily =' not in content:
    content = content.replace("const resetMode = inject('resetMode');", "const resetMode = inject('resetMode');\nconst isDaily = computed(() => resetMode.value === 'daily');")

content = content.replace('resetMode === "daily"', "isDaily")
content = content.replace("resetMode === 'daily'", "isDaily")

with open('src/pages/Dashboard.vue', 'w', encoding='utf-8') as f:
    f.write(content)
