from flask import Flask, request, render_template, jsonify
import logging
from chatbot import HealthcareChatbot  # Assuming the chatbot code is saved as `chatbot.py`

app = Flask(__name__)
chatbot = HealthcareChatbot()

# Route for the main chatbot page
@app.route('/')
def index():
    return render_template('index.html')

# Route to handle chatbot messages
@app.route('/chat', methods=['POST'])
def chat():
    user_input = request.json.get('message', '')
    response = chatbot.process_response(user_input)
    # Preserve newline characters in the response
    return jsonify({'response': response.replace('\n', '<br>')})

if __name__ == '__main__':
    app.run(debug=True)
