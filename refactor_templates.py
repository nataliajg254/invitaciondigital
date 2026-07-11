import re
import sys
import os

templates = [
    'templates/xv_natali/index.html',
    'templates/boda_elegante/index.html',
    'templates/generica/index.html',
]

for filepath in templates:
    if not os.path.exists(filepath):
        print(f"{filepath} no existe, saltando...")
        continue
        
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if '{% for section_name in ordered_sections %}' in content:
        print(f"{filepath} already refactored.")
        continue

    # Sections map
    sections = [
        ('countdown', r'{%\s*if invitation\.show_countdown\s*%}'),
        ('location', r'{%\s*if invitation\.show_location\s*%}'),
        ('program', r'{%\s*if invitation\.show_program\s+and\s+invitation\.program_events\.exists\s*%}'),
        ('parents', r'{%\s*if invitation\.show_parents\s+and\s+invitation\.parents\.exists\s*%}'),
        ('sponsors', r'{%\s*if invitation\.show_sponsors\s+and\s+invitation\.sponsors\.exists\s*%}'),
        ('gallery', r'{%\s*if invitation\.show_gallery\s+and\s+invitation\.gallery_items\.exists\s*%}'),
        ('gift_table', r'{%\s*if invitation\.show_gift_table\s+and\s+invitation\.gift_registries\.exists\s*%}'),
        ('dress_code', r'{%\s*if invitation\.show_dress_code\s+and\s+invitation\.dress_code\s*%}'),
        ('rsvp', r'{%\s*if invitation\.show_rsvp\s*%}'),
    ]

    header_end = content.find('</header>') + len('</header>')
    endblock_pos = content.find('{% endblock %}', header_end)
    
    pre_content = content[:header_end]
    post_content = content[endblock_pos:]
    mid_content = content[header_end:endblock_pos]

    # Find the positions of all sections
    pos_map = []
    for s_name, regex in sections:
        match = re.search(regex, mid_content)
        if match:
            # Need to find the start of the comment block right before it if it exists
            # We'll just look back up to 60 chars for "<!--"
            start_idx = match.start()
            comment_search = mid_content.rfind('<!--', max(0, start_idx - 60), start_idx)
            if comment_search != -1:
                start_idx = comment_search
            pos_map.append((start_idx, s_name, match.group(0)))
    
    # Sort positions
    pos_map.sort(key=lambda x: x[0])
    
    if not pos_map:
        print(f"No sections found in {filepath}")
        continue
        
    # Now build the new mid_content
    new_mid = "\n\n{% for section_name in ordered_sections %}\n"
    
    for i in range(len(pos_map)):
        start_idx = pos_map[i][0]
        s_name = pos_map[i][1]
        
        # End index is the start of the next section, or the end of mid_content
        if i < len(pos_map) - 1:
            end_idx = pos_map[i+1][0]
        else:
            end_idx = len(mid_content)
        
        section_html = mid_content[start_idx:end_idx]
        
        # Wrap it
        if i == 0:
            new_mid += f"    {{% if section_name == '{s_name}' %}}\n"
        else:
            new_mid += f"    {{% elif section_name == '{s_name}' %}}\n"
        
        new_mid += section_html.rstrip() + "\n"
        
    new_mid += "{% endif %}\n{% endfor %}\n\n"
    
    new_content = pre_content + new_mid + post_content
    
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(new_content)
        print(f"Refactored {filepath}")
