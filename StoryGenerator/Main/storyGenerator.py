import os
import json
import google.generativeai as genai
from dotenv import load_dotenv

# Load API key
load_dotenv(os.path.join(os.path.dirname(__file__), "api_key", ".env"))
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

def load_prompt(path="prompts/prompt.txt"):
    with open(path, "r", encoding="utf-8") as f:
        return f.read()

def save_story(data, filename):
    with open(f"output/{filename}.json", "w") as f:
        json.dump(data, f)
    return f"output/{filename}.json"

def main():
    print("--- AI Story Generator ---")
    
    grade = input("Enter grade level: ")
    difficulty = input("Enter difficulty: ")
    theme = input("Enter theme: ")

    prompt = load_prompt().format(grade=grade, difficulty=difficulty, theme=theme)

    model = genai.GenerativeModel("gemini-1.5-flash")
    print("\nGenerating story...")

    try:
        response = model.generate_content(prompt, generation_config={"response_mime_type": "application/json", "temperature": 0.8})
        story_data = json.loads(response.text)
        
        file_path = save_story(story_data, theme)
        print(f"Story saved to: {file_path}")
        print("\n--- Your Story ---")
        print(f"Title: {story_data.get('title', 'No Title')}")
        print("\nContent:\n" + story_data.get('content', '').replace('\\n\\n', '\n\n'))

    except json.JSONDecodeError:
        print("Error: Invalid JSON response from model.")
    except Exception as e:
        print("Error:", e)

if __name__ == "__main__":
    main()