document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generate-button');
    const generateForm = document.getElementById('generateForm'); // Get the form element
    const backstoryInput = document.getElementById('backstory');
    const samplesInput = document.getElementById('samples');
    const promptInput = document.getElementById('prompt');
    const generatedContentDiv = document.getElementById('generatedContent');
    const copyButton = document.getElementById('copy-button');
    let csrfToken;

    function getCookie(name) {
        const value = `; ${document.cookie}`;
        const parts = value.split(`; ${name}=`);
        if (parts.length === 2) return parts.pop().split(';').shift();
    }

    function fetchCsrfToken() {
        return fetch('https://aighostwriter.kurtastarita.com/csrf_token')
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                csrfToken = data.csrf_token;
                console.log('CSRF Token fetched:', csrfToken);
                // The token is also set as a cookie
                // Only attach the submit listener after the token is fetched
                generateForm.addEventListener('submit', generateContent);
            })
            .catch(error => {
                console.error('Error fetching CSRF token:', error);
                alert('Failed to fetch CSRF token. The application might not work correctly.');
                // Optionally, disable the generate button here
                if (generateButton) {
                    generateButton.disabled = true;
                }
            });
    }

    function generateContent(event) {
        event.preventDefault(); // Prevent default form submission
        const backstory = backstoryInput.value;
        const samples = samplesInput.value;
        const prompt = promptInput.value;
        const csrfTokenFromCookie = getCookie('csrf_token'); // Get the token from the cookie

        generateButton.classList.add('generating');
        generateButton.disabled = true;
        if (copyButton) {
            copyButton.style.display = 'none';
        }
        generatedContentDiv.textContent = '';

        if (!csrfTokenFromCookie) {
            console.error('CSRF token cookie not found. Cannot submit form.');
            alert('CSRF token cookie is missing. Please refresh the page.');
            generateButton.classList.remove('generating');
            generateButton.disabled = false;
            return;
        }

        const formData = new FormData(generateForm); // Use FormData to easily include the token
        formData.append('csrf_token', csrfTokenFromCookie); // Add the token to the form data

        fetch('https://aighostwriter.kurtastarita.com/generate', {
            method: 'POST',
            body: formData, // Send as form data
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
            generateButton.classList.remove('generating');
            generateButton.disabled = false;
            generatedContentDiv.textContent = data.generated_content;
            if (copyButton && data.generated_content) {
                copyButton.style.display = 'inline-block';
            }
        })
        .catch(error => {
            generateButton.classList.remove('generating');
            generateButton.disabled = false;
            generatedContentDiv.textContent = 'Error generating content. Please try again.';
            console.error('Error generating content:', error);
        });
    }

    // Call fetchCsrfToken when the page loads, and the submit listener will be attached after it completes
    fetchCsrfToken();
});
