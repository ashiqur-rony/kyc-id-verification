# Verify ID
A proof of concept API for verifying user's ID with a selfie and reading the information from the ID card.

## Installation
The API requires Python 3.9 or higher. Additional dependencies are listed in the `requirements.txt` file.

## Frontend
The frontend is built with HTML/JS and can be found in the `frontend` directory. Update the API URL at `line 11` in the `frontend/resources/js/app.js` file.

## Usage
1. Run the API server with `python app.py`.
2. Open the `index.html` file in the `frontend` directory in a browser.
3. Upload an image of your ID card and a selfie.
4. Click the `Verify` button to verify the ID.
5. The result will be displayed on the page.

## Deployment
Check for the build status at: https://builder.iabsis.com/build/.  
Once the build is successful, to build debian package, run `apt update` and then `apt install id-verification` from command line.
Once build is successful, the APP will be deployed to the server at https://id-verification.dev.oniabsis.com/.
