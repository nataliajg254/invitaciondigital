import os

filepath = 'templates/xv_natali/index.html'

with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

old_hero_content = """    .hero-content {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(10px);
        padding: 3rem 2rem; /* Adjusted for mobile */
        border-radius: 20px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        max-width: 90%;
    }
    
    .hero h1 {
        font-family: 'Great Vibes', cursive;
        font-size: clamp(4rem, 12vw, 6rem); /* Responsive font size slightly larger for cursive */
        font-weight: normal;
        margin-bottom: 0;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }
    
    .hero .subtitle {
        font-size: 1.5rem;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 2rem;
    }"""

new_hero_content = """    .hero-content {
        padding: 2rem 1rem;
        max-width: 100%;
        width: 100%;
    }
    
    .hero h1 {
        font-family: 'Great Vibes', cursive;
        font-size: clamp(4.5rem, 15vw, 7.5rem);
        font-weight: normal;
        margin-bottom: 0;
        text-shadow: 2px 4px 10px rgba(0,0,0,0.7);
        line-height: 1.2;
    }
    
    .hero .subtitle {
        font-size: 1.5rem;
        letter-spacing: 5px;
        text-transform: uppercase;
        margin-bottom: 1rem;
        text-shadow: 2px 4px 10px rgba(0,0,0,0.7);
    }
    
    .hero .elegant-font {
        text-shadow: 2px 4px 10px rgba(0,0,0,0.7);
        font-size: 1.6rem !important;
    }"""

content = content.replace(old_hero_content, new_hero_content)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
    print(f"Updated {filepath}")
