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
genai.configure(api_key="API")

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


#for the DietPro+
@app.route('/submit', methods=['POST'])
def submit():
    # Get form data
    name = request.form['name']
    age = request.form['age']
    gender = request.form['gender']
    medical_condition = request.form['medical_condition']
    food_preference = request.form['food_preference']
    food_allergies = request.form['food_allergies']
    preferred_language = request.form['preferred_language']

    # Create the prompt
    prompt = (
        f"Name: {name}, Age: {age}, Gender: {gender}, Medical Conditions: {medical_condition}, "
        f"Food Preferences: {food_preference}, Food Allergies: {food_allergies}, Preferred Language: {preferred_language}"
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
                "parts": ["Let's create a personalized food plan. Please provide the details."]
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
def medipalbot(prompt):

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "Context:\nYou are a Health Bot specializing in answering general questions about healthcare, diseases, medications, and related topics. You provide information in a user-friendly, accurate, and professional manner in the language specified by the user.\n\nObjective:\nTo assist users by answering their healthcare-related queries comprehensively, accurately, and in their preferred language. This includes providing information about diseases, symptoms, medications, treatments, and preventive care.\n\nUser Inputs:\nQuery: The user provides a health-related question (e.g., \"What are the symptoms of diabetes?\", \"What is the dosage for ibuprofen?\", or \"How to prevent high blood pressure?\").\nUser-Specified Language: The user specifies the language in which they want the response (e.g., English, Spanish, Hindi, etc.).\nOptional Context: Additional details about the user’s condition, medication, or health history to personalize the response (optional).\nOutput:\nDetailed Answer:\n\nProvide a comprehensive yet concise explanation tailored to the user’s query.\nInclude relevant examples, conditions, or references where applicable.\nEnsure clarity and accessibility in the user-specified language.\nMedication Details (if applicable):\n\nExplain the use, dosage, and side effects of the medication.\nHighlight contraindications or conditions when the medication should not be taken.\nDisease Information (if applicable):\n\nDescribe the disease or condition, including symptoms, causes, and treatments.\nSuggest preventive measures and lifestyle adjustments, if relevant.\nGeneral Health Tips (if applicable):\n\nProvide advice related to the query (e.g., dietary recommendations, exercise tips, or mental health practices).\nProfessional Disclaimer:\n\nInclude a note encouraging users to consult a healthcare professional for personalized advice or emergencies.\nStyle/Tone:\nEmpathetic & Supportive: Address the user’s concerns with care and understanding.\nProfessional & Informative: Provide accurate, medically sound information.\nLanguage Adaptability: Ensure the response is written in clear and appropriate language based on the user’s preference.\nOutput Format:\nGreeting and Acknowledgment:\n\nExample: “Hello! I’m here to help with your healthcare query. Let’s address your concern in [User-Specified Language].”\nDetailed Answer:\n\nInclude an easy-to-understand explanation of the topic.\nProvide actionable recommendations where applicable.\nAdditional Tips:\n\nOptional: Add health or wellness tips relevant to the query.\nProfessional Disclaimer:\n\nExample: “Please note that this information is for general purposes only. Consult a healthcare professional for detailed advice.”\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "Okay, I'm ready to answer health-related questions. Please provide the user's query, the desired language, and any optional context.  I will then provide a response following the specified format.\n",
                ],
            },
        ]
    )
    response = chat_session.send_message(prompt)
    return response.text

#  for NutriScan+
def scan_image_and_get_nutrition(image_path,language):
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
        response = chat_session.send_message(f"Please analyze the food and provide nutritional details in {language}.")
        # Render the result page with the response
        return response.text

    except Exception as e:
        print(f"Error during image processing: {e}")
        return f"An error occurred while processing the image: {str(e)}"

#for ReportCare+
def Analyse_reports(image_path,language):
    try:
        print(f"Processing image: {image_path}")  # Log the image path

        # Upload image to Gemini
        uploaded_file = upload_to_gemini(image_path, mime_type="image/png")
        if not uploaded_file:
            raise Exception("File upload to Gemini failed")

        print(f"Uploaded file URI: {uploaded_file.uri}")  # Log the file URI

        # Start the chat session with Gemini
        chat_session = model.start_chat(
            history=[
                {
                    "role": "user",
                    "parts": [
                        f"Context:\nYou are a medical report analyzer tasked with reviewing and providing assistance based on the medical reports provided by users. Your goal is to help users understand their medical conditions, medications, test results, and dietary recommendations, offering clear and empathetic guidance.\n\nObjective:\nAssist users by interpreting their medical reports and providing relevant information and recommendations regarding their condition, medication, food, and test results.\n\nDetails and Requirements:\n\nUser Inputs:\nMedical Reports: (Any medical reports, including test results, prescriptions, X-rays, blood/urine reports, etc.)\nUser Information: (Optional: Details like age, gender, medical history, allergies, or other relevant personal information that could help in the analysis.)\nOutput:\nMedical Condition Explanation:\n\nProvide a clear and simple explanation of the medical condition(s) identified in the report (e.g., hypertension, diabetes, etc.).\nOffer general information on how the condition affects the body and potential risks if not managed properly.\nMedication Explanation:\n\nExplain the prescribed medications, including the purpose of each, how they work, and their potential side effects.\nClarify any specific instructions, such as dosage, frequency, and timing.\nDietary Recommendations:\n\nSuggest foods to consume and avoid based on the medical condition(s) and medications (e.g., \"Eat more fiber-rich foods for diabetes\" or \"Avoid high-sodium foods for hypertension\").\nProvide meal planning suggestions, ensuring they align with the medical needs.\nMedication Schedule:\n\nProvide a clear schedule for taking medications (e.g., \"Take Medication X in the morning with food,\" \"Medication Y should be taken 30 minutes before meals\").\nOffer any special instructions regarding the timing of medications in relation to meals or other medications.\nX-ray Explanation (if applicable):\n\nProvide details and interpretation of the X-ray results, explaining what the images show (e.g., \"The X-ray indicates mild lung inflammation\").\nAdvise on follow-up actions or treatments based on the results.\nBlood/Urine Test Results Explanation (if applicable):\n\nReview blood or urine test results, explaining each of the markers and what they indicate (e.g., \"Your cholesterol levels are elevated, indicating a need to manage your diet and lifestyle\").\nOffer guidance on what actions to take based on abnormal results (e.g., \"Increase your water intake for better kidney function\").\nStyle/Tone:\nEmpathetic: Provide a supportive tone, recognizing that medical reports can be overwhelming and ensuring that the user feels cared for.\nProfessional and Clear: Use simple, understandable language while maintaining accuracy in medical explanations.\nGuiding and Reassuring: Offer advice and support without causing alarm, focusing on next steps and positive actions.\nOutput Format/Deliverables:\nA clear, structured report summarizing:\nThe medical condition(s).\nExplanation of medications and their schedules.\nDietary recommendations.\nInsights from test results and X-rays, along with actionable steps.\nA concise medication schedule.\nDietary do’s and don’ts tailored to the user's condition.",
                    ],
                },
                {
                    "role": "model",
                    "parts": [
                        "Please provide me with the medical reports and any relevant user information (age, gender, medical history, allergies, etc.).  I need this information to generate a personalized report based on your specific situation.  I will then provide a clear, empathetic, and comprehensive analysis as requested.\n"
                    ],
                },
                {
                    "role": "user",
                    "parts": [uploaded_file],
                }]
        )

        # Send a message to the chat session (can include more context if required)
        response = chat_session.send_message(f"Please analyze the report and , try to provide details in user preferred language {language},You try best in providing in user preferd language else incase ou cant provide in english.")
        # Render the result page with the response
        return response.text

    except Exception as e:
        print(f"Error during image processing: {e}")
        return f"An error occurred while processing the image: {str(e)}"


#for QuickDiagnose+
def diagnose(image_path,language):
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
                    "Context:\nYou are an AI-powered doctor tasked with assisting users by providing general treatment advice, diagnosing potential diseases based on symptoms or images, and suggesting appropriate medications for common conditions. You will provide these details in the user’s preferred language.\n\nObjective:\nHelp the user by analyzing symptoms or images, providing a possible diagnosis, recommending general treatment, and listing common medications that may be used to treat the condition (for informational purposes).\n\nDetails and Requirements:\n\nUser Inputs:\nSymptoms (or Image of the Condition):\nA description of the symptoms the user is experiencing (e.g., fever, cough, fatigue, pain) or an image showing the condition.\nPatient Details (Optional):\nAge, gender, medical history, and any other relevant details to tailor the advice.\nPreferred Language:\nThe language in which the diagnosis, treatment, and medication details should be provided (e.g., English, Spanish, Hindi, etc.).\nOutput:\nPossible Diagnosis:\n\nBased on the symptoms or image, suggest a possible disease or condition the person might be suffering from (e.g., \"The symptoms point towards a potential flu infection\" or \"The image indicates a possible skin rash due to eczema\").\nProvide general information about the disease and how it affects the body.\nGeneral Treatment Advice:\n\nOffer general treatment steps for managing the symptoms or condition (e.g., \"Rest, stay hydrated, and take over-the-counter pain relievers for fever\" or \"Apply a topical cream to soothe the skin rash\").\nSuggest lifestyle modifications or preventive measures that could help in managing or curing the condition (e.g., \"Avoid cold foods and stay warm for better recovery\").\nMedication Suggestions (For Informational Purposes):\n\nList common medications that are typically prescribed for the condition (e.g., \"For flu, doctors often recommend taking paracetamol for fever and ibuprofen for body aches\").\nProvide information on dosage and frequency as typically recommended by healthcare providers (e.g., \"Take one tablet of paracetamol every 4-6 hours, as needed\").\nInclude common over-the-counter (OTC) medications and/or prescription medications used for the disease (e.g., \"Antihistamines may be prescribed for allergic reactions\").\nAdditional Notes:\n\nMention any warning signs or red flags for when the user should consult a healthcare professional (e.g., \"If symptoms worsen or if you experience difficulty breathing, please seek immediate medical attention\").\nProvide advice on when to seek professional medical help based on the severity or progression of symptoms.\nStyle/Tone:\nEmpathetic and Supportive: Recognize that the user might be worried about their health and provide reassurance with clear, helpful guidance.\nProfessional and Accurate: Provide medically informed advice and treatment suggestions based on the symptoms or image, ensuring it aligns with general practices.\nClear and User-Friendly: Use simple language and avoid complex medical jargon so that users can easily understand the information.\nOutput Format/Deliverables:\nA diagnosis or possible disease, with a brief description.\nTreatment advice tailored to the condition.\nA list of common medications for the condition, including dosages and frequency.\nA warning if the user should see a healthcare professional or if their condition could escalate.",
                ],
            },
                {
                    "role": "model",
                    "parts": [
                        "Please provide me with the user's symptoms, optional patient details (age, gender, medical history), and preferred language.  I need this information to provide a helpful and accurate response.  I will then offer a possible diagnosis, treatment advice, medication suggestions (for informational purposes only), and warnings as requested.  Remember, I am an AI and cannot replace a doctor.  This information is for general knowledge and informational purposes only.\n"
                    ],
                },
                {
                    "role": "user",
                    "parts": [uploaded_file],
                }]
        )

        # Send a message to the chat session (can include more context if required)
        response = chat_session.send_message(f"Please analyze the image and provide information About the condition in {language}.")
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
    preferred_language = request.form['language']
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
            analysis_result = scan_image_and_get_nutrition(image_filename,preferred_language)

            # Store the result in session for the results page
            session['result'] = analysis_result

            # Redirect to results page
            return redirect(url_for('result'))

        except Exception as e:
            print(f"Error during image processing: {e}")
            return jsonify({'error': f'Error during image processing: {str(e)}'}), 500

    return jsonify({'error': 'No image file found in the request.'}), 400

@app.route('/scan_report', methods=['POST'])
def scan_report():
    preferred_language = request.form['language']
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
            analysis_result = Analyse_reports(image_filename,preferred_language)

            # Store the result in session for the results page
            session['result'] = analysis_result

            # Redirect to results page
            return redirect(url_for('result'))

        except Exception as e:
            print(f"Error during image processing: {e}")
            return jsonify({'error': f'Error during image processing: {str(e)}'}), 500

    return jsonify({'error': 'No image file found in the request.'}), 400


@app.route('/quick_diagnose', methods=['POST'])
def quick_diagnose():
    preferred_language = request.form['language']
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
            analysis_result = diagnose(image_filename,preferred_language)

            # Store the result in session for the results page
            session['result'] = analysis_result

            # Redirect to results page
            return redirect(url_for('result'))

        except Exception as e:
            print(f"Error during image processing: {e}")
            return jsonify({'error': f'Error during image processing: {str(e)}'}), 500

    return jsonify({'error': 'No image file found in the request.'}), 400
#medipal bot
@app.route('/medipal', methods=['GET', 'POST'])
def medipal():
    if request.method == 'GET':
        return render_template('medipal.html')
    elif request.method == 'POST':
        user_input = request.json.get("query")
        language = request.json.get("language", "English")
        context = request.json.get("context", "")

        if not user_input:
            return jsonify({"error": "Query is required"}), 400

        try:
            message = f"Query: {user_input}\nLanguage: {language}\nContext: {context}"
            # Replace the following with your chatbot integration logic
            response_content = medipalbot(message)
            return jsonify({"response": response_content })
        except Exception as e:
            return jsonify({"error": str(e)}), 500

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
