const form = document.getElementById('verifyForm');

if (!_api_key) {
    console.log('API key not found');
}

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
            document.getElementById('resultContent').innerHTML = text;

            let id_type = '';
            let id_number = '';
            let mrz = '';
            let contains_dob = false;
            let valid_govt_id = false;
            let dob = '';
            let age = 0;

            console.log('Success:', text);

            json_msg = JSON.parse(text);

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
                let formattedHTML = '<ul>';
                if (id_type !== '') {
                    formattedHTML += '<li>ID Type: ' + id_type + '</li>';
                }
                if (id_number !== '') {
                    formattedHTML += '<li>ID Number: ' + id_number + '</li>';
                }
                if (mrz !== '') {
                    formattedHTML += '<li>Machine Readable Zone: ' + htmlEncode(mrz) + '</li>';
                }
                if (contains_dob) {
                    formattedHTML += '<li>Date of Birth: ' + dob + '</li>';
                }
                if (valid_govt_id) {
                    formattedHTML += '<li>Valid Govt. ID: Yes</li>';
                } else {
                    formattedHTML += '<li>Valid Govt. ID: No</li>';
                }
                formattedHTML += '</ul>';
                document.getElementById('resultData').innerHTML = formattedHTML;
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
    const birthDate = new Date(dateOfBirth);

    let age = today.getFullYear() - birthDate.getFullYear();
    const monthDiff = today.getMonth() - birthDate.getMonth();

    // Adjust age if birthday hasn't happened yet this year
    if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
        age--;
    }

    return age;
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
