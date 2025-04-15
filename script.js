document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generate-button');
    const backstoryInput = document.getElementById('backstory');
    const samplesInput = document.getElementById('samples');
    const promptInput = document.getElementById('prompt');
    const generatedContentDiv = document.getElementById('generatedContent');
    const buttonLoadingIndicator = document.getElementById('button-loading-indicator'); // For the button spinner
    const copyButton = document.getElementById('copy-button'); // Assuming you have a copy button
    const copyLoadingIndicator = document.getElementById('copy-loading-indicator'); // For the copy spinner
    let csrfToken; // Variable to store the CSRF token

    function generateContent() {
        const backstory = backstoryInput.value;
        const samples = samplesInput.value;
        const prompt = promptInput.value;

        // Show loading state for generate button
        generateButton.disabled = true;
        if (buttonLoadingIndicator) {
            buttonLoadingIndicator.style.display = 'inline-block'; // Or 'block' depending on your styling
        }
        if (copyButton) {
            copyButton.style.display = 'none';
        }
        if (copyLoadingIndicator) {
            copyLoadingIndicator.style.display = 'none';
        }
        generatedContentDiv.textContent = '';

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
            // Hide loading state and show content/copy button
            generateButton.disabled = false;
            if (buttonLoadingIndicator) {
                buttonLoadingIndicator.style.display = 'none';
            }
            generatedContentDiv.textContent = data.generated_content;
            if (copyButton && data.generated_content) {
                copyButton.style.display = 'inline-block'; // Or 'block'
            }
        })
        .catch(error => {
            // Hide loading state and show error
            generateButton.disabled = false;
            if (buttonLoadingIndicator) {
                buttonLoadingIndicator.style.display = 'none';
            }
            generatedContentDiv.textContent = 'Error generating content. Please try again.';
            console.error('Error generating content:', error);
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

    // Add event listener for copy button (if it exists)
    if (copyButton) {
        copyButton.addEventListener('click', function() {
            const textToCopy = generatedContentDiv.textContent;
            if (textToCopy) {
                // Show loading state for copy button
                copyButton.disabled = true;
                if (copyLoadingIndicator) {
                    copyLoadingIndicator.style.display = 'inline-block'; // Or 'block'
                }

                navigator.clipboard.writeText(textToCopy)
                    .then(() => {
                        // Hide loading state and re-enable button
                        copyButton.disabled = false;
                        if (copyLoadingIndicator) {
                            copyLoadingIndicator.style.display = 'none';
                        }
                        alert('Content copied to clipboard!');
                    })
                    .catch(err => {
                        console.error('Failed to copy text: ', err);
                        // Hide loading state and re-enable button
                        copyButton.disabled = false;
                        if (copyLoadingIndicator) {
                            copyLoadingIndicator.style.display = 'none';
                        }
                        alert('Failed to copy content.');
                    });
            } else {
                alert('No content to copy.');
            }
        });
    }
});
