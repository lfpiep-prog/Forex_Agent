
import os
import google.generativeai as genai
from dotenv import load_dotenv
import logging

# Load environment variables
load_dotenv()

logger = logging.getLogger("GeminiAssistant")
logging.basicConfig(level=logging.INFO)

class GeminiAssistant:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            logger.error("GOOGLE_API_KEY not found in environment variables.")
            raise ValueError("GOOGLE_API_KEY not found.")
        
        genai.configure(api_key=self.api_key)
        self.model = genai.GenerativeModel(model_name)
        logger.info(f"GeminiAssistant initialized with model: {model_name}")

    def generate_content(self, prompt):
        """
        Generates content using the Gemini model.
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating content: {e}")
            return f"Error: {str(e)}"

    def explain_file(self, file_path):
        """
        Reads a file and asks Gemini to explain it.
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            prompt = f"Please explain the following code/document and summarize its purpose:\n\n{content}"
            return self.generate_content(prompt)
        except FileNotFoundError:
            return f"File not found: {file_path}"
        except Exception as e:
            return f"Error reading file: {e}"

    def ask_about_project(self, question, context_files=[]):
        """
        Asks a question about the project, optionally providing context files.
        """
        context = ""
        for file_path in context_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_content = f.read()
                    context += f"\n--- File: {file_path} ---\n{file_content}\n"
            except Exception as e:
                logger.warning(f"Could not read context file {file_path}: {e}")

        prompt = f"Context:\n{context}\n\nQuestion: {question}"
        return self.generate_content(prompt)

if __name__ == "__main__":
    # Simple test if run directly
    try:
        assistant = GeminiAssistant()
        print("Gemini Assistant initialized successfully.")
        response = assistant.generate_content("Hello, introduce yourself briefly.")
        print(f"Response: {response}")
    except Exception as e:
        print(f"Initialization failed: {e}")
