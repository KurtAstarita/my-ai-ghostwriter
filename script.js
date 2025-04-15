document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generate-button');
    const backstoryInput = document.getElementById('backstory');
    const samplesInput = document.getElementById('samples');
    const promptInput = document.getElementById('prompt');
    const generatedContentDiv = document.getElementById('generatedContent');
    const loadingIndicator = document.getElementById('loading-indicator'); // Make sure you have an element with this ID in your HTML
    let csrfToken; // Variable to store the CSRF token

    function generateContent() {
        const backstory = backstoryInput.value;
        const samples = samplesInput.value;
        const prompt = promptInput.value;

        // Show loading indicator
        generatedContentDiv.textContent = ''; // Clear previous content
        loadingIndicator.textContent = 'Loading...';
        loadingIndicator.style.display = 'block'; // Make it visible

        fetch('https://my-ai-ghostwriter.onrender.com/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                // 'X-CSRFToken': csrfToken, // If you re-enable CSRF
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
            loadingIndicator.style.display = 'none'; // Hide loading indicator
            generatedContentDiv.textContent = data.generated_content;
        })
        .catch(error => {
            console.error('Error generating content:', error);
            loadingIndicator.style.display = 'none'; // Hide loading indicator on error
            generatedContentDiv.textContent = 'Error generating content. Please try again.';
        });
    }

    // Fetch CSRF token on page load (even if disabled on backend for now)
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
