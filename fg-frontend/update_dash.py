with open('src/pages/Dashboard.vue', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('<h2>Fluid Intake for Today</h2>', '<h2>{{ resetMode === "daily" ? "Fluid Intake for Today" : "Fluid Intake for the Period" }}</h2>')

with open('src/pages/Dashboard.vue', 'w', encoding='utf-8') as f:
    f.write(content)
