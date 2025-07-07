from flask import Flask, jsonify
from flask_cors import CORS
import json
import os
import lib.IDVerification as Verify
import lib.LLM as llm
import lib.Mindee as mnd
import lib.Forgery as forgery
from lib.Logging import Logging, log
from lib.ImageModels import IMDModel
from flask import request
from dotenv import load_dotenv
import time

app = Flask(__name__)
CORS(app)

logging = Logging()

load_dotenv()
gemini_api_key = os.getenv('GEMINI_API_KEY')
mindee_api_key = os.getenv('MINDEE_API_KEY')
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
    document = request.form.get('document')
    method = request.form.get('method')

    if not os.path.exists(app.config['UPLOAD_FOLDER']):
        os.makedirs('uploads', exist_ok=True)

    if not id_image or not selfie_image:
        return jsonify({'code': 0, 'message': 'Please provide both picture of ID and a picture to compare.'}), 400

    id_path = f'{app.config["UPLOAD_FOLDER"]}/id_{time.time_ns()}_{id_image.filename}'
    picture_path = f'{app.config["UPLOAD_FOLDER"]}/selfie_{time.time_ns()}_{selfie_image.filename}'

    id_image.save(id_path)
    print(f'Saved ID image to {id_path}')
    selfie_image.save(picture_path)
    print(f'Saved selfie image to {picture_path}')

    # Check if the ID is tampered
    forgery_detector = forgery.Forgery(id_path)
    check_for_tampering, metadata, forgery_model_score, noise_forgery, cluster_forgery_score = forgery_detector.detect()
    if check_for_tampering:
        # Delete the ID and selfie images before returning the error
        os.remove(id_path)
        os.remove(picture_path)
        return jsonify({'code': 1, 'message': 'ID is tampered or forged.', 'metadata_score': metadata,
                        'forgery_model_score': forgery_model_score, 'noise_forgery': noise_forgery,
                        'cluster_forgery_score': cluster_forgery_score}), 400


    id_reader = Verify.IDVerification()
    try:
        id_match = id_reader.match_id_with_picture(id_path, picture_path)
    except Exception as e:
        # Delete the ID and selfie images before returning the error
        os.remove(id_path)
        os.remove(picture_path)
        return jsonify({'code': 3, 'message': f'Error: {str(e)}', 'metadata_score': metadata,
                        'forgery_model_score': forgery_model_score, 'noise_forgery': noise_forgery,
                        'cluster_forgery_score': cluster_forgery_score}), 500

    return_data = {
        'code': 4,
        'forged': check_for_tampering,
        'face_match': False,
        'data_found': False,
        'metadata_score': metadata,
        'forgery_model_score': forgery_model_score,
        'noise_forgery': noise_forgery,
        'cluster_forgery_score': cluster_forgery_score
    }

    if id_match and json.loads(id_match)['match']:
        return_data['face_match'] = True
        try:
            id_data = None
            if method == 'gemini':
                llm_match = llm.LLM(name='gemini', id_path=id_path, api_key=gemini_api_key)
                id_data = llm_match.read_id_data_with_gemini()
            elif method == 'mindee':
                mindee_match = mnd.Mindee(id_path=id_path, api_key=mindee_api_key)
                id_data = mindee_match.read_id_data()
        except Exception as e:
            # Delete the ID and selfie images before returning the error
            os.remove(id_path)
            os.remove(picture_path)
            return_data['message'] = f'Error: {str(e)}'
            return jsonify(return_data), 500

        if id_data:
            return_data['code'] = 4
            return_data['data_found'] = True
            return_data['message'] = 'ID verification successful.'
            return_data['data'] = id_data
        else:
            return_data['code'] = 5
            return_data['message'] = 'ID matched the image.'
            return_data['data'] = 'No data found.'
    else:
        return_data['code'] = 6
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
        f.readline()  # Skip the header
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
