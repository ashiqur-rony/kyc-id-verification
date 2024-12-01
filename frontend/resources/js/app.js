const form = document.getElementById('verifyForm');

form.addEventListener('submit', (event) => {
    event.preventDefault(); // Prevent default form submission
    document.getElementById('loading').classList.remove('hidden');
    document.getElementById('result').classList.add('hidden');
    document.getElementById('resultContent').innerHTML = '';

    const formData = new FormData(form);

    fetch('http://localhost:8080/api/v1/verify', {
        method: 'POST',
        body: formData
    })
        .then(response => response.text())
        .then(text => {
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('result').classList.remove('hidden');
            document.getElementById('resultContent').innerHTML = text;

            console.log('Success:', text);

            json_msg = JSON.parse(text);
            data = json_msg['data'];

            message = json_msg['message'];
            console.log('Data:', data);

            console.log('Message:', message);
        })
        .catch(error => {
            document.getElementById('result').classList.remove('hidden');
            document.getElementById('loading').classList.add('hidden');
            document.getElementById('resultContent').innerHTML = error;
            console.error('Error uploading file:', error);
        });
});
