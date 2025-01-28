from flask import Flask, render_template, request, redirect, url_for, jsonify, session
import google.generativeai as genai
import os
from PIL import Image
import secrets  # To generate a secret key

# Configure the generative AI API
app = Flask(__name__)

# Set a secret key for session management (use a random key for development or production)
app.secret_key = secrets.token_hex(16)  # Generates a random secret key

# Configure your API key here
genai.configure(api_key="AIzaSyCV7pLU5IN8btkJ72BjLxK547cMc1lJOGY")

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
)

UPLOAD_FOLDER = 'uploads/'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/dietpro')
def dietpro():
    return render_template('dietpro.html')


@app.route('/nutriscan')
def nutriscan():
    return render_template('nutriscan.html')


@app.route('/reportcare')
def reportcare():
    return render_template('reportcare.html')


@app.route('/quickdiagnose')
def quickdiagnose():
    return render_template('quickdiagnose.html')


@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    name = request.form.get('name')
    age = request.form.get('age')
    medical_condition = request.form.get('medical_condition')
    food_preference = request.form.get('food_preference')
    food_allergies = request.form.get('food_allergies')
    preferred_language = request.form.get('preferred_language')

    # Check if required fields are missing (optional validation)
    if not (name and age and preferred_language):
        return "Missing required fields", 400

    # Create the prompt specific to pregnant women
    prompt = (
        f"User Details:\n"
        f"Name: {name}, Age: {age}, Medical Conditions: {medical_condition}, "
        f"Food Preferences: {food_preference}, Food Allergies: {food_allergies}, Preferred Language: {preferred_language}\n\n"
        f"Context:\n"
        f"You are a nutrition specialist tasked with creating a personalized dietary plan for a pregnant woman. "
        f"The user is pregnant and requires a diet that provides essential nutrients for both the mother and baby. "
        f"Ensure that the plan considers the user's medical conditions, food preferences, and food allergies. "
        f"Deliver the plan in the user's preferred language and include recommended quantities of each item."
        f"Do not give unnessecary details, only provide the food list with recommended quantities."
    )

    # Start the chat session with Gemini model
    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "Context:\nYou are a nutrition specialist tasked with providing personalized dietary recommendations based on user inputs.\n\n"
                    "Objective:\nCreate a food list that aligns with the user’s details, medical condition, food preferences, food allergies, and is delivered in the user’s specified language, complete with recommended quantities wherever possible."
                ]
            },
            {
                "role": "model",
                "parts": ["Let's create a personalized food plan for a pregnant woman. Please provide the details."]
            },
            {
                "role": "user",
                "parts": [prompt]
            },
        ]
    )

    # Get the response from the model
    response = chat_session.send_message(prompt)

    # Render the result page with the response
    return render_template('result.html', response_text=response.text)


# Function to handle image and chat session for NutriScan
def scan_image_and_get_nutrition(image_path):
    try:
        print(f"Processing image: {image_path}")  # Log the image path

        # Upload image to Gemini
        uploaded_file = upload_to_gemini(image_path, mime_type="image/png")
        if not uploaded_file:
            raise Exception("File upload to Gemini failed")

        print(f"Uploaded file URI: {uploaded_file.uri}")  # Log the file URI

        # Start the chat session with Gemini
        chat_session = model.start_chat(
            history=[{
                "role": "user",
                "parts": [
                    "Context:\nYou are a nutrition analyzer tasked with identifying and providing nutritional details based on an image of food provided by the user.\n\nObjective:\nAnalyze the image to identify the food items, suggest improvements based on the user’s information (e.g., dietary needs, medical conditions, food preferences), and provide an approximation of the nutrients present in the food."
                ],
            },
                {
                    "role": "model",
                    "parts": [
                        "Let's analyze the food in the image and provide nutritional details."
                    ],
                },
                {
                    "role": "user",
                    "parts": [uploaded_file],
                }]
        )

        # Send a message to the chat session (can include more context if required)
        response = chat_session.send_message("Please analyze the food and provide nutritional details for a Pregnent lady with provided Medical conditions")
        # Render the result page with the response
        return response.text

    except Exception as e:
        print(f"Error during image processing: {e}")
        return f"An error occurred while processing the image: {str(e)}"


def upload_to_gemini(path, mime_type=None):
    """Uploads the given file to Gemini."""
    try:
        print(f"Uploading file: {path}, MIME type: {mime_type}")  # Add logging
        file = genai.upload_file(path, mime_type=mime_type)
        print(f"Uploaded file '{file.display_name}' as: {file.uri}")
        return file
    except Exception as e:
        print(f"Error uploading the file: {e}")
        return None


# Route to handle image upload and analysis
@app.route('/scan_image', methods=['POST'])
def scan_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image file found'}), 400

    image = request.files['image']
    if image:
        # Validate file type
        if not image.filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            return jsonify({'error': 'Invalid file type. Please upload a PNG, JPG, or JPEG image.'}), 400

        try:
            # Save the image to the uploads folder
            image_filename = os.path.join(app.config['UPLOAD_FOLDER'], image.filename)
            image.save(image_filename)

            # Log the file path for debugging
            print(f"Image saved to: {image_filename}")

            # Call function to analyze the image and get the nutritional details
            analysis_result = scan_image_and_get_nutrition(image_filename)

            # Store the result in session for the results page
            session['result'] = analysis_result

            # Redirect to results page
            return redirect(url_for('result'))

        except Exception as e:
            print(f"Error during image processing: {e}")
            return jsonify({'error': f'Error during image processing: {str(e)}'}), 500

    return jsonify({'error': 'No image file found in the request.'}), 400


@app.route('/result')
def result():
    # Fetch the result from the session
    result = session.get('result')
    if result:
        return render_template('result.html', response_text=result)
    else:
        return render_template('result.html', response_text="No result found.")

if __name__ == '__main__':
    app.run(debug=True)
