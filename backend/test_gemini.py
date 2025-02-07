import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure Gemini API
genai.configure(api_key=os.getenv('GEMINI_API_KEY'))

def test_translation():
    try:
        # Initialize Gemini
        model = genai.GenerativeModel('gemini-pro')
        
        # Test translation
        text = "Hello, how are you?"
        prompt = f"Translate the following English text to Spanish: '{text}'"
        
        response = model.generate_content(prompt)
        print("Original text:", text)
        print("Translation:", response.text)
        print("\nGemini API is working correctly!")
        return True
    except Exception as e:
        print(f"Error with Gemini API: {str(e)}")
        return False

if __name__ == "__main__":
    test_translation() 