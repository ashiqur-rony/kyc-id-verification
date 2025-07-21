const form = document.getElementById('verifyForm');

if (!_api_key) {
    console.log('API key not found');
}

// --- Configuration ---
// The formats we will attempt to parse, in order of preference.
// You can add, remove, or reorder formats here.
// This handles the ambiguity of formats like DD/MM vs MM/DD.
const SUPPORTED_FORMATS = [
    'YYYY-MM-DD',
    'YYYY/MM/DD',
    'DD/MM/YYYY',
    'DD-MM-YYYY',
    'MM-DD-YYYY',
    'MM/DD/YYYY'
];

form.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent default form submission
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('resultContent').innerHTML = '';

    const formData = new FormData(form);

    fetch('/api/v1/verify', {
        method: 'POST',
        body: formData,
        headers: {
            'Authorization': 'Bearer ' + _api_key
        }
    })
        .then(response => response.text())
        .then(text => {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('result').classList.remove('hidden');
            document.getElementById('resultContent').innerHTML = htmlEncode(text);

            let id_type = '';
            let id_number = '';
            let mrz = '';
            let contains_dob = false;
            let valid_govt_id = false;
            let dob = '';
            let age = 0;

            console.log('Success:', text);

            json_msg = JSON.parse(text);

            let formattedHTML = '<ul>';
            formattedHTML += '<li>Metadata Score: ' + json_msg['metadata_score'] + '</li>';
            formattedHTML += '<li>Model Score: ' + json_msg['forgery_model_score'] + '</li>';
            formattedHTML += '<li>Noise Score: ' + json_msg['noise_forgery'] + '</li>';
            formattedHTML += '<li>Cluster Score: ' + json_msg['cluster_forgery_score'] + '</li>';

            if (json_msg['data_found']) {

                data = json_msg['data'];

                parsed_data = JSON.parse(data);
                if (parsed_data.hasOwnProperty('ID Type')) {
                    id_type = parsed_data['ID Type'];
                }
                if (parsed_data.hasOwnProperty('ID Number')) {
                    id_number = parsed_data['ID Number'];
                }
                if (parsed_data.hasOwnProperty('Machine Readable Zone')) {
                    mrz = parsed_data['Machine Readable Zone'];
                }
                if (parsed_data.hasOwnProperty('Contains DOB') && parsed_data['Contains DOB'].toLowerCase() === 'yes') {
                    if (parsed_data.hasOwnProperty('Date of Birth (DOB)') && parsed_data['Date of Birth (DOB)'] !== '') {
                        dob = parsed_data['Date of Birth (DOB)'];
                        contains_dob = true;
                        age = calculateAge(dob);
                    }
                }
                if (parsed_data.hasOwnProperty('Valid Govt. ID') && parsed_data['Valid Govt. ID'].toLowerCase() === 'yes') {
                    valid_govt_id = true;
                }

                message = json_msg['message'];
                console.log('Data:', data);

                console.log('Message:', message);

                // Display DOB verification result
                document.getElementById('resultOutput').classList.remove('invalid');
                document.getElementById('resultOutput').classList.remove('verify');
                document.getElementById('resultOutput').classList.remove('valid');

                if (contains_dob) {

                    if (valid_govt_id && age >= 18) {
                        document.getElementById('resultOutput').innerHTML = 'Face matched with ID photo.<br>Verified age: ' + age + ' years<br>Verified Govt. ID: ' + id_type;
                        document.getElementById('resultOutput').classList.add('valid');
                    } else if (valid_govt_id && age < 18) {
                        document.getElementById('resultOutput').innerHTML = 'Face matched with ID photo.<br>Verified age: ' + age + ' years<br>Verified Govt. ID: ' + id_type;
                        document.getElementById('resultOutput').classList.add('invalid');
                    } else if (!valid_govt_id && age >= 18) {
                        document.getElementById('resultOutput').innerHTML = 'Face matched with ID photo.<br>Verified age: ' + age + ' years<br>Invalid Govt. ID: ' + id_type;
                        document.getElementById('resultOutput').classList.add('verify');
                    } else {
                        document.getElementById('resultOutput').innerHTML = 'Face matched with ID photo.<br>Verified age: ' + age + ' years<br>Invalid Govt. ID: ' + id_type;
                        document.getElementById('resultOutput').classList.add('invalid');
                    }
                } else {
                    document.getElementById('resultOutput').innerHTML = 'Face matched with ID photo.<br>Date of Birth not found.';
                    document.getElementById('resultOutput').classList.add('invalid');
                }

                // Display formatted data

                if (id_type !== '') {
                    formattedHTML += '<li>ID Type: ' + id_type + '</li>';
                }
                if (id_number !== '') {
                    formattedHTML += '<li>ID Number: ' + id_number + '</li>';
                }
                if (contains_dob) {
                    formattedHTML += '<li>Date of Birth: ' + dob + '</li>';
                }
                if (valid_govt_id) {
                    formattedHTML += '<li>Valid Govt. ID: Yes</li>';
                } else {
                    formattedHTML += '<li>Valid Govt. ID: No</li>';
                }
            } else if (json_msg['face_match']) {
                document.getElementById('resultOutput').innerHTML = 'Face matched with ID photo.<br>Could not verify age.';
                document.getElementById('resultOutput').classList.add('verify');
            } else if (parseInt(json_msg['code']) < 4) {
                let message = 'Error occurred with the ID validation with error code: ' + json_msg['code'] + '.<br>Please try again later.';
                if (json_msg['message']) {
                    message = json_msg['message'];
                }
                document.getElementById('resultOutput').innerHTML = message;
                document.getElementById('resultOutput').classList.add('invalid');
            } else {
                document.getElementById('resultOutput').innerHTML = 'Face did not match the ID photo.<br>No data parsed.';
                document.getElementById('resultOutput').classList.add('invalid');
            }

            formattedHTML += '</ul>';
            document.getElementById('resultData').innerHTML = formattedHTML;
        })
        .catch(error => {
            document.getElementById('result').classList.remove('hidden');
            document.getElementById('loading').classList.add('hidden');
            // document.getElementById('resultContent').innerHTML = error;
            console.error('Error uploading file:', error);
        });
});

function calculateAge(dateOfBirth) {
    const today = new Date();
    const birthDate = parseArbitraryDate(dateOfBirth);

    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    // Adjust age if birthday hasn't happened yet this year
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }

    return age;
}

/**
 * Tries to parse a date string by attempting a list of supported formats.
 * @param {string} dateString The string to parse.
 * @returns {Date|null} A valid Date object or null if parsing fails.
 */
function parseArbitraryDate(dateString) {
    for (const format of SUPPORTED_FORMATS) {
        const parts = getPartsFromFormat(dateString, format);

        // If parts were successfully extracted for the current format
        if (parts) {
            const { year, month, day } = parts;

            // Create a date object. We use Date.UTC to work with dates in a timezone-agnostic way,
            // preventing issues where the user's local timezone might shift the date.
            const date = new Date(Date.UTC(year, month - 1, day));

            // --- Validation Step ---
            // This is crucial. It checks if the created date is valid. For example, if the input was
            // '2023-02-30', new Date() would create '2023-03-02' (it "rolls over").
            // This check ensures the day, month, and year haven't changed.
            if (date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day) {
                // Success! We found a valid format.
                console.log('Date matched format:', format);
                return date;
            }
        }
    }

    return null;
}

/**
 * A helper function to extract year, month, and day from a string based on a format specifier.
 * @param {string} dateString The input date string (e.g., "21/07/2024").
 * @param {string} format The format specifier (e.g., 'DD/MM/YYYY').
 * @returns {{year: number, month: number, day: number}|null} An object with parts, or null if it doesn't match.
 */
function getPartsFromFormat(dateString, format) {
    // Use a regex to split by a hyphen or a slash.
    const formatParts = format.split(/[-/]/);
    const dateParts = dateString.split(/[-/]/);

    // The number of parts must match (e.g., 3 parts for date, 3 for format).
    if (formatParts.length !== dateParts.length) {
        return null;
    }

    const parts = {};
    for (let i = 0; i < formatParts.length; i++) {
        // Assign the numeric part to the correct key (year, month, or day)
        const key = formatParts[i].toLowerCase();
        parts[key] = parseInt(dateParts[i], 10);
    }

    // If any part is not a number, the format is incorrect.
    if (isNaN(parts.year) || isNaN(parts.month) || isNaN(parts.day)) {
        return null;
    }

    return { year: parts.year, month: parts.month, day: parts.day };
}

function htmlEncode(str) {
    // Replace < with &lt;
    str = str.replace(/</g, "&lt;");
    // Replace > with &gt;
    str = str.replace(/>/g, "&gt;");
    // Replace & with &amp;
    str = str.replace(/&/g, "&amp;");
    return str;
}
