import re

with open('src/App.vue', 'r', encoding='utf-8') as f:
    content = f.read()

dropdown_old = re.search(r'<button \s*@click="toggleTheme".*?<span>\{\{ isDarkMode \? \'Light Mode\' : \'Dark Mode\' \}\}</span>\s*</button>', content, re.DOTALL)
if dropdown_old:
    dropdown_new = '''<button 
                  @click="() => { navigateTo('preferences'); isUserMenuOpen = false; }"
                  class="dropdown-action-btn"
                >
                  <svg class="icon-svg" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
                  <span>Preferences</span>
                </button>'''
    content = content.replace(dropdown_old.group(0), dropdown_new)
    print('Replaced dropdown')

if '<Preferences' not in content:
    content = content.replace('<Reports v-else />', '<Preferences v-else-if="currentPage === \'preferences\'" />\n      <Reports v-else />')

with open('src/App.vue', 'w', encoding='utf-8') as f:
    f.write(content)
