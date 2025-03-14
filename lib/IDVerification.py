import face_recognition
import os
import json
import re
import datetime


class IDVerification:
    """
    IDVerification class to compare faces in ID images with faces in provided pictures and extract text from ID images.
    """

    def __init__(self):
        """
        Initialize the IDVerification class with the Gemini API key.
        """
        # self.gemini_api_key = api_key
        pass

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
