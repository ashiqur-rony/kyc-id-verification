import google.generativeai as genai
import json
import os
import re
import datetime
from lib.Logging import Logging, log


class LLM:
    def __init__(self, name, id_path, api_key=None):
        self.name = name
        self.id_path = id_path
        self.api_key = api_key
        logging = Logging()

    def read_id_data(self):
        if self.name == 'gemini':
            return self.read_id_data_with_gemini()

    def read_id_data_with_gemini(self):
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
        genai.configure(api_key=self.api_key)
        # model = genai.GenerativeModel('gemini-1.5-flash')
        model = genai.GenerativeModel('gemini-2.0-flash')
        file = genai.upload_file(self.id_path)

        prompt = (
            "Please extract and parse the text from the ID card image. "
            "Ensure the extracted information is formatted for database entry with the following fields: "
            "ID Type, Name, Address, Date of Birth (DOB), Expiration Date (EXP), Machine Readable Zone, and any other relevant details. "
            "ID Type can be either of Driving License, Passport, Govt. ID, and Other. "
            "Also include if this is a valid government-issued ID and contains date of birth (DOB). "
            "Finally, document can contain signs of manipulation or forgery. Often forged documents have obvious marks like font mismatch or color imbalance. Look for signs of forgery and report whether it is forged or not. "
            "Provide the output in a structured JSON format without any backticks. "
            "Example format: "
            "{"
            "\"ID Type\": \"Driving License\", "
            "\"Name\": \"John Doe\", "
            "\"Address\": \"123 Main St, Any town, USA\", "
            "\"Date of Birth (DOB)\": \"01/01/1970\", "
            "\"Expiration Date (EXP)\": \"01/01/2030\", "
            "\"Driver's License Number\": \"D1234567\", "
            "\"Passport Number\": \"D1234567\", "
            "\"ID Number\": \"D1234567\", "
            "\"Nationality\": \"France\", "
            "\"Class\": \"C\", "
            "\"Sex\": \"M\", "
            "\"Height\": \"6'-0\"\", "
            "\"Weight\": \"180 lb\", "
            "\"Eyes\": \"BLU\", "
            "\"Restrictions\": \"NONE\", "
            "\"Endorsements\": \"NONE\", "
            "\"Issue Date\": \"01/01/2020\", "
            "\"Donor\": \"Yes\", "
            "\"Valid Govt. ID\": \"Yes\", "
            "\"Contains DOB\": \"Yes\", "
            "\"Forged\": \"No\", "
            "\"Machine Readable Zone\": \"<MRZ>\""
            "}"
        )

        self.__log(f'Extracting text from ID card image: {self.id_path}')

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
        log(message, print_console)  # Use the log function from the Logging module
