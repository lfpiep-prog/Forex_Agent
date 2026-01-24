
import os
import sys

# Add project root to path to verify imports work as expected
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools.gemini_assistant import GeminiAssistant

def main():
    print("--- Starting Gemini API Demo ---")
    
    try:
        # Initialize
        assistant = GeminiAssistant()
        print("1. Authentication: SUCCESS")
        
        # Test 1: Simple Generation
        print("\n2. Testing Simple Chat...")
        response = assistant.generate_content("What are three key benefits of using Python for data science? Keep it brief.")
        print(f"Gemini Response:\n{response}")
        
        # Test 2: File Explanation (README.md)
        readme_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "README.md")
        if os.path.exists(readme_path):
            print(f"\n3. Testing File Explanation ({readme_path})...")
            summary = assistant.explain_file(readme_path)
            print(f"Summary of README:\n{summary}")
        else:
            print(f"\n3. Skipping File Explanation - README.md not found at {readme_path}")
            
        print("\n--- Demo Completed Successfully ---")
        
    except Exception as e:
        print(f"\n!!! Demo FAILED !!!")
        print(f"Error: {e}")

if __name__ == "__main__":
    main()
