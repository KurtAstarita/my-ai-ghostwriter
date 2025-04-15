document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generate-button');
    const backstoryInput = document.getElementById('backstory');
    const samplesInput = document.getElementById('samples');
    const promptInput = document.getElementById('prompt');
    const generatedContentDiv = document.getElementById('generated-content');

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function generateContent() {
        const backstory = backstoryInput.value;
        const samples = samplesInput.value;
        const prompt = promptInput.value;
        const csrfToken = getCookie('csrf_token'); // Get the CSRF token from the cookie

        fetch('https://my-ai-ghostwriter.onrender.com/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Include the CSRF token in the header
            },
            body: JSON.stringify({ backstory, samples, prompt }),
        })
        .then(response => {
            if (!response.ok) {
                return response.text().then(text => {
                    throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
                });
            }
            return response.json();
        })
        .then(data => {
            generatedContentDiv.textContent = data.generated_content;
        })
        .catch(error => {
            console.error('Error generating content:', error);
            generatedContentDiv.textContent = 'Error generating content. Please try again.';
        });
    }

    // Fetch CSRF token on page load
    fetch('https://my-ai-ghostwriter.onrender.com/csrf_token')
    .then(response => {
        if (!response.ok) {
            return response.text().then(text => {
                throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
            });
        }
        return response.json(); // We might not need the JSON response itself
    })
    .then(() => {
        generateButton.addEventListener('click', generateContent);
    })
    .catch(error => {
        console.error('Error fetching CSRF token:', error);
    });
});
