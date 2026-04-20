import re
from pathlib import Path

# Character data with roles and details
characters = {
    'luffy': {'role': 'captain', 'title': 'Captain', 'bounty': '3,000,000,000'},
    'zoro': {'role': 'swordsman', 'title': 'Swordsman', 'bounty': '1,111,000,000'},
    'nami': {'role': 'navigator', 'title': 'Navigator', 'bounty': '366,000,000'},
    'usopp': {'role': 'sniper', 'title': 'Sniper', 'bounty': '500,000,000'},
    'sanji': {'role': 'cook', 'title': 'Cook', 'bounty': '1,032,000,000'},
    'chopper': {'role': 'doctor', 'title': 'Doctor', 'bounty': '1,000,000,000'},
    'robin': {'role': 'archaeologist', 'title': 'Archaeologist', 'bounty': '930,000,000'},
    'franky': {'role': 'shipwright', 'title': 'Shipwright', 'bounty': '394,000,000'},
    'brook': {'role': 'musician', 'title': 'Musician', 'bounty': '383,000,000'},
}

file_path = Path('html/characters.html')
content = file_path.read_text(encoding='utf-8')

# Replace character detail sections with proper grid cards
for char_id, data in characters.items():
    # Pattern to find and replace each character section
    pattern = rf'<section id="{char_id}" class="character-detail">(.*?)</section>'
    
    role = data['role']
    title = data['title']
    bounty = data['bounty']
    
    replacement = f'''<div class="crew-card" data-role="{role}" data-name="{char_id}">
            <a href="{char_id}.html" class="crew-card-link">
                <div class="crew-card-image">
                    <img src="../images/{char_id}.jfif" alt="{char_id.replace('_', ' ').title()}" loading="lazy">
                </div>
                <div class="crew-card-content">
                    <span class="crew-role-badge">{title}</span>
                    <h3 class="crew-card-name">{char_id.replace('_', ' ').title().replace('Usopp', 'Usopp').replace('Chopper', 'Tony Tony Chopper').replace('Robin', 'Nico Robin').replace('Franky', 'Franky').replace('Brook', 'Brook').replace('Sanji', 'Sanji').replace('Nami', 'Nami').replace('Zoro', 'Roronoa Zoro').replace('Luffy', 'Monkey D. Luffy')}</h3>
                    <p class="crew-bounty">💰 {bounty} Berries</p>
                    <span class="crew-cta">View Profile</span>
                </div>
            </a>
        </div>'''
    
    content = re.sub(pattern, replacement, content, flags=re.DOTALL)

# Close the characters-grid section properly
content = content.replace('</section>\n\n        <!-- Zoro -->', '')
content = content.replace('</section>\n\n        <!-- Nami -->', '')
content = content.replace('</section>\n\n        <!-- Usopp -->', '')
content = content.replace('</section>\n\n        <!-- Sanji -->', '')
content = content.replace('</section>\n\n        <!-- Chopper -->', '')
content = content.replace('</section>\n\n        <!-- Robin -->', '')
content = content.replace('</section>\n\n        <!-- Franky -->', '')
content = content.replace('</section>\n\n        <!-- Brook -->', '')

# Add footer
if '</main>' in content:
    footer = '''    <footer>
        <p style="font-size: 1.3em; letter-spacing: 2px; margin-bottom: 20px;">STRAW HAT CREW</p>
        <p>The strongest pirates ever to sail the Grand Line</p>
        
        <div class="footer-divider"></div>
        
        <p style="margin-bottom: 5px;">
            <strong>Explore:</strong> 
            <a href="index.html">Story Arcs</a> • 
            <a href="devil-fruits.html">Devil Fruits</a> • 
            <a href="characters.html">Crew Members</a>
        </p>
        
        <div class="footer-divider"></div>
        
        <div class="footer-credits">
            <p>🏴‍☠️ The legendary Straw Hat Pirate Crew, led by Monkey D. Luffy</p>
            <p style="margin-top: 10px; opacity: 0.6;">© 2026 One Piece Explorer | Set Sail! 🗺️</p>
        </div>
    </footer>

    <div class="footer-actions">
        <a href="#top" class="back-to-top">Back to top</a>
    </div>

    <script src="../js/script.js"></script>
</body>
</html>'''
    content = content.replace('</main>', f'        </section>\n    </main>\n\n{footer}')

file_path.write_text(content, encoding='utf-8')
print('Updated characters.html with enhanced crew cards and filtering')
