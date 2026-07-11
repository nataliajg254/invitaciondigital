import os

templates = [
    'templates/xv_natali/index.html',
    'templates/boda_elegante/index.html',
    'templates/generica/index.html',
]

media_query = """
    /* Mobile Parallax Fix: Disable fixed background on mobile for smooth scrolling */
    @media (max-width: 768px) {
        .hero {
            background-attachment: scroll !important;
        }
        .floral-bg, .bg-light, .bg-white, .minimal-card, .bg-dark {
            background-attachment: scroll !important;
        }
    }
</style>
"""

for filepath in templates:
    if not os.path.exists(filepath):
        continue

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'Mobile Parallax Fix' not in content:
        content = content.replace('</style>', media_query)

    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
        print(f"Updated {filepath}")
