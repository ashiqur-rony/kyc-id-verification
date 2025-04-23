"""
Mindee API integration for ID card text extraction.
This module provides the Mindee class to extract and parse the text from the ID card image.
Requires the Mindee API key to be set in the environment variable MINDEE_API_KEY.
"""
from mindee import Client, product, AsyncPredictResponse
import json
import os
import re
import datetime
from lib.Logging import Logging, log


class Mindee:
    def __init__(self, id_path, api_key=None):
        self.id_path = id_path
        self.api_key = api_key
        logging = Logging()

    def read_id_data(self):
        return self.read_id_data_with_mindee()

    def read_id_data_with_mindee(self):
        """
        Extract and parse the text from the ID card image.
        :param id_path: string path to the ID image
        :return: string JSON response with ID information
        """
        mindee_client = Client(api_key=self.api_key)
        file = mindee_client.source_from_path(self.id_path)

        self.__log(f'Extracting text from ID card image: {self.id_path}')

        response: AsyncPredictResponse = mindee_client.enqueue_and_parse(
            product.InternationalIdV2,
            file,
        )

        response_document = response.document

        self.__log(f'Response from Mindee API: {str(response_document)}', print_console=True)

        return self.clean_result_text(str(response_document))

    def clean_result_text(self, result_text):
        """
        :param result_text: JSON response from the Mindee API
        :return: string cleaned JSON response
        """
        data = {}
        for line in result_text.split('\n'):
            if line.startswith(':'):
                items = line.split(':')
                if len(items) < 2:
                    continue
                key = items[1].strip()
                value = items[2].strip()
                data[key] = value

        self.__log(f'Extracted data: {data}', print_console=True)

        cleaned_text = {
            'ID Type': data['Document Type'] if 'Document Type' in data else 'Other',
            'Name': data['Given Names'] + ' ' + data['Surnames'] if 'Given Names' in data else '',
            'Address': data['Address'] if 'Address' in data else '',
            'Date of Birth (DOB)': data['Birth Date'] if 'Birth Date' in data else '',
            'Expiration Date (EXP)': data['Expiration Date'] if 'Expiration Date' in data else '',
            'ID Number': data['Document Number'] if 'Document Number' in data else '',
            'Valid Govt. ID': 'Yes' if 'Document Type' in data else 'No',
            'Contains DOB': 'Yes' if 'Birth Date' in data else 'No',
            'Machine Readable Zone': data['MRZ Line 1'] + data['MRZ Line 2'] + data['MRZ Line 3'] if 'MRZ Line 1' in data else '',
        }

        return json.dumps(cleaned_text)

    def __log(self, message, print_console=False):
        """
        Log the message to the console.
        :param message: string message to log
        """
        log(message, print_console)  # Use the log function from the Logging module
