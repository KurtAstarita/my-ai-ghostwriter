document.addEventListener('DOMContentLoaded', function() {
    const generateButton = document.getElementById('generate-button');
    const backstoryInput = document.getElementById('backstory');
    const samplesInput = document.getElementById('samples');
    const promptInput = document.getElementById('prompt');
    const generatedContentDiv = document.getElementById('generatedContent');
    const copyButton = document.getElementById('copy-button');
    let csrfToken; // Variable to store the CSRF token

    // Function to fetch the CSRF token
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
                // Store it in localStorage as a fallback in case of Render inactivity?
                localStorage.setItem('csrf_token', csrfToken);
            })
            .catch(error => {
                console.error('Error fetching CSRF token:', error);
                // Try to get it from localStorage as a fallback
                csrfToken = localStorage.getItem('csrf_token');
                if (!csrfToken) {
                    alert('Failed to fetch CSRF token. The application might not work correctly.');
                } else {
                    console.warn('Using CSRF token from localStorage.');
                }
            });
    }

    function generateContent() {
        const backstory = backstoryInput.value;
        const samples = samplesInput.value;
        const prompt = promptInput.value;

        generateButton.classList.add('generating');
        generateButton.disabled = true;
        if (copyButton) {
            copyButton.style.display = 'none';
        }
        generatedContentDiv.textContent = '';

        fetch('https://aighostwriter.kurtastarita.com/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken, // Include the CSRF token as a header
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

    generateButton.addEventListener('click', generateContent);

  if (copyButton) {
    copyButton.addEventListener('click', function() {
      const textToCopy = generatedContentDiv.textContent;
      if (textToCopy) {
        // Show loading state for copy button
        copyButton.disabled = true;
        generatedContentDiv.classList.add('loading');

        navigator.clipboard.writeText(textToCopy)
          .then(() => {
            // Hide loading state and re-enable button
            copyButton.disabled = false;
            generatedContentDiv.classList.remove('loading');
            alert('Content copied to clipboard!');
          })
          .catch(err => {
            console.error('Failed to copy text: ', err);
            // Hide loading state and re-enable button
            generatedContentDiv.classList.remove('loading');
            alert('Failed to copy content.');
          });
      } else {
        alert('No content to copy.');
      }
    });
  }
    fetchCsrfToken();
});
