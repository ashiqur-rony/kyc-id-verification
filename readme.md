# KYC ID Verification and Forgery Detection
A proof of concept framework for verifying user's ID with a selfie 
using image processing and deep learning models.  
The frontend interface receives the user's ID and selfie image and 
sends to the Python bakcend using API. The backend process verifies the 
ID for possible forgery and checks if the selfie matches the ID. The 
result is sent back to the frontend for display.  

![KYC Workflow](figures%2Fkyc-verification-workflow.jpg)  
_Figure: KYC Verification Workflow_

## Implementation Overview

### Forgery Detection
The forgery detection consists of two steps. The **first step** uses 
traditional image processing techniques for SIFT anomaly detection. 
Additionally, this step checks for the presence of image manipulation 
software signature/metadata.

The **second step** uses clustering to identify noise variance. Finally,
a deep learning (DL) model trained on manipulated images identifies 
whether if the image was manipulated. ELA (Error Level Analysis) image is 
used for this DL model. The model training steps can be found on 
[Kaggel](https://www.kaggle.com/code/ghumkumar/image-manipulation-detection-model).

Finally, all the results from the above steps are combined using 
various weights to give a final forgery detection result.

### Selfie Verification
If the ID is verified to be authentic, the next step is to verify if 
the selfie matches the ID. We used the `face_recognition` library to 
match if the face in the selfie matches the face in the ID.

### Reading User Information
Instead of using traditional OCR, we used LLMs to read the user 
information. For this proof-of-concept, we implemented Gemini and 
Mindee APIs. This step reads user's biographic information from the ID 
including date of birth and machine readable zone (MRZ). This step also 
predicts whether the ID is government issued or not.

### Results
A user level survey with both authentic and manipulated IDs showed 73% 
accuracy in forgery detection.

---

## Setting up the Environment

### Installation
1. The API requires Python 3.9 or higher. Additional dependencies are listed in the `requirements.txt` file.
2. Rename `.env-dist` to `.env`.
3. Add the API keys for Gemini and Mindee in the `.env` file.

### Frontend
1. The frontend is built with HTML/JS and can be found in the `frontend` directory. 
2. Rename the `key.js-dist` to `key.js`.
3. Update the API URL in the `key.js` file.

### Usage
1. Run the API server with `python app.py`.
2. Open the `index.html` file in the `frontend` directory in a browser.
3. Upload an image of your ID card and a selfie.
4. Click the `Verify` button to verify the ID.
5. The result will be displayed on the page.

---

### File Structure
```
|-- app.py                  # Main API server
|-- requirements.txt        # Python dependencies
|-- .env-dist               # Environment variables template
|-- readme.md               # This file
|-- figures/                # Figures for the readme
|-- frontend/               # Frontend user interface in HTML/JS
|   |-- index.html          # Main HTML file
|   |resources/             # CSS and JS resources
|   |   |...
|   |   |js/                # JavaScript files
|   |   |-- key.js-dist     # API URL configuration template
|--lib/                     # Python libraries for image processing and deep learning
|   |-- model/              # Pre-trained deep learning models for forgery detection