import re

filepath = 'templates/xv_natali/index.html'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Add load static if not exists
if '{% load static %}' not in content:
    content = content.replace('{% extends \'base.html\' %}', '{% extends \'base.html\' %}\n{% load static %}')

# Add CSS class
css = '''
    .floral-bg {
        background-image: url("{% static 'img/fondo_floral.png' %}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
    }
'''
if '.floral-bg' not in content:
    content = content.replace('</style>', css + '</style>')

# Replace section classes
# For sections that are NOT bg-dark
def repl(m):
    tag = m.group(0)
    if 'bg-dark' in tag:
        return tag
    
    # Remove bg-light and bg-white if present
    tag = tag.replace('bg-light', '').replace('bg-white', '')
    
    if 'class="' in tag:
        tag = tag.replace('class="', 'class="floral-bg ')
    else:
        tag = tag.replace('>', ' class="floral-bg">')
    return tag

new_content = re.sub(r'<section id="[^"]+"[^>]*>', repl, content)

# Clean up extra spaces in class
new_content = new_content.replace('class="floral-bg  "', 'class="floral-bg"').replace('class="floral-bg "', 'class="floral-bg"')

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(new_content)
print('Done.')
