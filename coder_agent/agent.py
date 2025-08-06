import os
from dotenv import load_dotenv
import re

# Load environment variables
load_dotenv()

def change_button_color():
    """Change the button color from blue to red in index.html"""
    
    html_file = "index.html"
    
    try:
        # Read the HTML file
        with open(html_file, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Replace blue background color with red
        updated_content = re.sub(
            r'background-color:\s*#007BFF;',
            'background-color: #DC3545;',
            content
        )
        
        # Write the updated content back to the file
        with open(html_file, 'w', encoding='utf-8') as file:
            file.write(updated_content)
        
        print("✅ Button color changed from blue to red!")
        print("🔄 Refresh your browser to see the changes.")
        
    except FileNotFoundError:
        print("❌ Error: index.html file not found!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🤖 Agent starting...")
    print("🎨 Changing button color from blue to red...")
    change_button_color()
