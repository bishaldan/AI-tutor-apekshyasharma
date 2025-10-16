import os
import json
import re

def sanitize_filename(theme):
    filename = f"{theme.replace(' ', '_').replace('/', '_').lower()}_story.json"
    filename = re.sub(r'[^\w\-_\.]', '', filename)
    return filename

def get_unique_filename(base_dir, base_name):
    counter = 1
    name, ext = os.path.splitext(base_name)
    filename = base_name
    while os.path.exists(os.path.join(base_dir, filename)):
        filename = f"{name}_{counter}{ext}"
        counter += 1
    return filename

def save_story_json(story_data, filename, output_dir="output"):
    os.makedirs(output_dir, exist_ok=True)
    file_path = os.path.join(output_dir, filename)
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(story_data, f, indent=4, ensure_ascii=False)
    return file_path
