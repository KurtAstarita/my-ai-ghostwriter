document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generate-button');
    const backstoryInput = document.getElementById('backstory');
    const samplesInput = document.getElementById('samples');
    const promptInput = document.getElementById('prompt');
    const generatedContentDiv = document.getElementById('generatedContent');
    let csrfToken; // Variable to store the CSRF token

    function generateContent() {
        const backstory = backstoryInput.value;
        const samples = samplesInput.value;
        const prompt = promptInput.value;

        fetch('https://my-ai-ghostwriter.onrender.com/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Use the fetched CSRF token
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
        return response.json();
    })
    .then(data => {
        csrfToken = data.csrf_token; // Store the CSRF token from the response
        generateButton.addEventListener('click', generateContent);
    })
    .catch(error => {
        console.error('Error fetching CSRF token:', error);
    });
});
