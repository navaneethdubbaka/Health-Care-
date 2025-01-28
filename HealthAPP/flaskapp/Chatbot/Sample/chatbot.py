import os
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any
import requests
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class HealthcareChatbot:
    def __init__(self):
        self.api_key = 'AIzaSyCT0NyOCyrKoH6UhX_pQmtUHBlQpvIIYqA'

    def get_gemini_response(self, query: str) -> str:
        try:
            url = 'https://generativelanguage.googleapis.com/v1/models/gemini-pro:generateContent'
            headers = {
                'Content-Type': 'application/json',
                'x-goog-api-key': self.api_key
            }

            data = {
                "contents": [{"parts": [{"text": query + ''' During pregnancy(You are a pregnancy-focused AI assistant. 
Generate plain text only. 
-Assist users with pregnancy-related questions and symptoms like vomiting, nausea, etc.
- Respond to greetings like "Hello," "Hi," etc., in a warm and friendly tone.
- For pregnancy-related questions or symptoms (vomiting, nausea, etc.), provide short, clear, and helpful information.   
- If the question is unrelated to pregnancy, respond with: "I am not able to generate these type of questions."  
)'''}]}]
            }

            response = requests.post(url, headers=headers, json=data)
            response.raise_for_status()

            response_data = response.json()
            if 'candidates' in response_data:
                return response_data['candidates'][0]['content']['parts'][0]['text']
            return "I am not able to generate a response for that query."

        except requests.exceptions.RequestException as e:
            logging.error(f"API request failed: {e}")
            return "An error occurred while contacting the API. Please try again later."

    def process_response(self, user_input: str) -> str:
        try:
            if not user_input.strip():
                return "Please ask a question."
            response = self.get_gemini_response(user_input)
            logging.info(f"Generated response for input: {user_input[:50]}...")
            return response
        except Exception as e:
            logging.error(f"Error processing response: {str(e)}")
            return "I apologize, but I encountered an error. Please try again."

def main():
    try:
        # Initialize chatbot
        healthcare_bot = HealthcareChatbot()

        print("\n=== HealthcareBot with Gemini API ===")
        print("Type 'exit' or 'quit' to end the session")
        print("Type 'help' for assistance")
        print("Ask any health-related questions!")
        print("====================================\n")

        session_start = datetime.now()

        while True:
            try:
                # Get user input
                user_input = input("You: ").strip()

                # Handle exit commands
                if user_input.lower() in ["exit", "quit"]:
                    session_duration = datetime.now() - session_start
                    print(f"\nSession Duration: {session_duration}")
                    print("HealthcareBot: Goodbye! Take care of your health!")
                    break

                # Process and display response
                response = healthcare_bot.process_response(user_input)
                print(f"HealthcareBot: {response}")

            except KeyboardInterrupt:
                print("\nHealthcareBot: Session interrupted. Goodbye!")
                break

    except Exception as e:
        logger.critical(f"Critical error in main loop: {str(e)}")
        print("\nAn unexpected error occurred. Please check the logs for details.")
        sys.exit(1)

if __name__ == "__main__":
    main()
