from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
import lib.IDVerification as Verify
from flask import request
from dotenv import load_dotenv
import time

app = Flask(__name__)
CORS(app)

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
upload_path = os.getenv('UPLOAD_PATH')

app.config['UPLOAD_FOLDER'] = upload_path


@app.route('/')
def hello_world():
    """
    Hello world route.
    :return: string JSON response
    """
    return json.dumps({'message': 'Hello!'})


@app.route('/api/v1/verify', methods=['POST'])
def verify():
    """
    Verify the ID card with the provided picture.
    :return: string JSON response
    """
    if not check_request(request):
        return jsonify({'message': 'Unauthorized request.'}), 401

    id_image = request.files['id_image']
    selfie_image = request.files['selfie_image']

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs('uploads', exist_ok=True)

    if not id_image or not selfie_image:
        return jsonify({'message': 'Please provide both picture of ID and a picture to compare.'}), 400

    id_path = f'{app.config["UPLOAD_FOLDER"]}/id_{time.time_ns()}_{id_image.filename}'
    picture_path = f'{app.config["UPLOAD_FOLDER"]}/selfie_{time.time_ns()}_{selfie_image.filename}'

    id_image.save(id_path)
    print(f'Saved ID image to {id_path}')
    selfie_image.save(picture_path)
    print(f'Saved selfie image to {picture_path}')

    id_reader = Verify.IDVerification(gemini_api_key)
    try:
        id_match = id_reader.match_id_with_picture(id_path, picture_path)
    except Exception as e:
        return jsonify({'message': f'Error: {str(e)}'}), 500

    return_data = {}

    if id_match and json.loads(id_match)['match']:
        try:
            id_data = id_reader.read_id_data(id_path)
        except Exception as e:
            return jsonify({'message': f'Error: {str(e)}'}), 500

        if id_data:
            return_data['message'] = 'ID verification successful.'
            return_data['data'] = id_data
        else:
            return_data['message'] = 'ID matched the image.'
            return_data['data'] = 'No data found.'
    else:
        return_data['message'] = 'ID verification failed.'
        return_data['data'] = 'No data found.'

    # Delete the ID and selfie images after processing
    os.remove(id_path)
    os.remove(picture_path)

    return jsonify(return_data), 200


def check_request(request):
    """
    Check if the request is authorized.
    :param request: request object
    :return: boolean
    """
    approved_origins = []

    with open('data/keys.csv', 'r') as f:
        f.readline()    # Skip the header
        while True:
            keys = f.readline()
            if not keys:
                break
            keys = keys.strip().split(',')
            approved_origins.append(
                {
                    'origin': keys[0],
                    'api_key': keys[1]
                }
            )


    auth_header = request.headers.get('Authorization')
    if auth_header and auth_header.startswith('Bearer '):
        api_key = auth_header.split(' ')[1]
        origin = request.headers.get('Origin').replace('http://', '').replace('https://', '')

        requester = next((app for app in approved_origins if origin in app['origin'] and api_key == app['api_key']),
                         None)
        if requester:
            return True

    return False


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
