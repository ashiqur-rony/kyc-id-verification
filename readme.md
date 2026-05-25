# Verify ID
A proof of concept API for verifying user's ID with a selfie and reading the information from the ID card.

## Installation
1. The API requires Python 3.9 or higher. Additional dependencies are listed in the `requirements.txt` file.
2. Rename `.env-dist` to `.env`.
3. Add the API keys for Gemini and Mindee in the `.env` file.

## Frontend
1. The frontend is built with HTML/JS and can be found in the `frontend` directory. 
2. Rename the `key.js-dist` to `key.js`.
3. Update the API URL in the `key.js` file.

## Usage
1. Run the API server with `python app.py`.
2. Open the `index.html` file in the `frontend` directory in a browser.
3. Upload an image of your ID card and a selfie.
4. Click the `Verify` button to verify the ID.
5. The result will be displayed on the page.
