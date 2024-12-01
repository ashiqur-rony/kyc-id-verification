import face_recognition
import os
import google.generativeai as genai
import json
import re
import datetime


class IDVerification:
    """
    IDVerification class to compare faces in ID images with faces in provided pictures and extract text from ID images.
    """

    def __init__(self, api_key=None):
        """
        Initialize the IDVerification class with the Gemini API key.
        """
        self.gemini_api_key = api_key

    def match_id_with_picture(self, id_path, picture_path):
        """
        Compare the face in the ID image with the face in the provided picture.
        :param id_path: string path to the ID image
        :param picture_path: string path to the picture to compare with
        :return: string JSON response
        """
        id_image = face_recognition.load_image_file(id_path)
        id_face_locations = face_recognition.face_locations(id_image)
        if len(id_face_locations) == 0:
            return json.dumps({'message': 'Cannot detect face in ID image.', 'score': 0, 'match': False})

        id_face_encodings = face_recognition.face_encodings(id_image, id_face_locations)[0]

        selfie_image = face_recognition.load_image_file(picture_path)
        selfie_face_locations = face_recognition.face_locations(selfie_image)
        if len(selfie_face_locations) == 0:
            return json.dumps({'message': 'Cannot detect face in provided picture.', 'score': 0, 'match': False})

        selfie_face_encodings = face_recognition.face_encodings(selfie_image, selfie_face_locations)[0]

        comparison = face_recognition.face_distance([id_face_encodings], selfie_face_encodings)

        self.__log(f'Face comparison score: {comparison[0]}', print_console=True)

        if comparison[0] < 0.6:
            return json.dumps({'message': 'Pictured matched with ID.', 'score': comparison[0], 'match': True})

        return json.dumps({'message': 'Picture did not match with ID.', 'score': comparison[0], 'match': False})

    def read_id_data(self, id_path):
        """
        Extract and parse the text from the ID card image.
        :param id_path: string path to the ID image
        :return: string JSON response with ID information

        Expected output:
            {
              "Name": "BERTHIER",
              "FirstName": "CORINNE",
              "Address": "PARIS 1ER (75)",
              "Date of Birth (DOB)": "06.12.1965",
              "National ID Number": "880692310285",
              "Sex": "F",
              "Height": "1M70",
              "Nationality": "Française"
            }
        """
        genai.configure(api_key=self.gemini_api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        file = genai.upload_file(id_path)

        prompt = (
            "Please extract and parse the text from the ID card image. "
            "Ensure the extracted information is formatted for database entry with the following fields: "
            "Name, Address, Date of Birth (DOB), Expiration Date (EXP), and any other relevant details. "
            "Provide the output in a structured JSON format without any backticks. "
            "Example format: "
            "{"
            "\"Name\": \"John Doe\", "
            "\"Address\": \"123 Main St, Any town, USA\", "
            "\"Date of Birth (DOB)\": \"01/01/1970\", "
            "\"Expiration Date (EXP)\": \"01/01/2030\", "
            "\"Driver's License Number\": \"D1234567\", "
            "\"Class\": \"C\", "
            "\"Sex\": \"M\", "
            "\"Height\": \"6'-0\"\", "
            "\"Weight\": \"180 lb\", "
            "\"Eyes\": \"BLU\", "
            "\"Restrictions\": \"NONE\", "
            "\"Endorsements\": \"NONE\", "
            "\"Issue Date\": \"01/01/2020\", "
            "\"Donor\": \"Yes\""
            "}"
        )

        self.__log(f'Extracting text from ID card image: {id_path}')

        response = model.generate_content([file, "\n\n", prompt])

        self.__log(f'Response from Gemini API: {response.text}', print_console=True)

        return self.clean_result_text(response.text)

    def clean_result_text(self, result_text):
        cleaned_text = re.sub(r'```json|```', '', result_text).strip()
        try:
            json.loads(cleaned_text)
        except json.JSONDecodeError:
            cleaned_text = re.sub(r'\\n', ' ', cleaned_text)
            cleaned_text = re.sub(r'\\', '', cleaned_text)
        return cleaned_text

    def __log(self, message, print_console=False):
        """
        Log the message to the console.
        :param message: string message to log
        """
        if not os.path.exists(os.path.join(os.getcwd(), 'logs')):
            os.makedirs('logs', exist_ok=True)

        current_date = datetime.datetime.now().strftime('%Y-%m-%d')
        with open(os.path.join('logs', f'id_verification_{current_date}.log'), 'a') as log_file:
            log_file.write(f'{datetime.datetime.now()} - {message}\n')

        if print_console:
            print(message)
