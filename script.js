document.addEventListener('DOMContentLoaded', function() {
  const generateButton = document.getElementById('generate-button');
  const backstoryInput = document.getElementById('backstory');
  const samplesInput = document.getElementById('samples');
  const promptInput = document.getElementById('prompt');
  const generatedContentDiv = document.getElementById('generatedContent');
  const copyButton = document.getElementById('copy-button'); // Assuming you have a copy button
  let csrfToken; // Variable to store the CSRF token

  function generateContent() {
    const backstory = backstoryInput.value;
    const samples = samplesInput.value;
    const prompt = promptInput.value;

    // Show loading state for generate button
    generateButton.classList.add('generating');
    generateButton.disabled = true;
    if (copyButton) {
      copyButton.style.display = 'none';
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
      generateButton.classList.remove('generating');
      generateButton.disabled = false;
      generatedContentDiv.textContent = data.generated_content;
      if (copyButton && data.generated_content) {
        copyButton.style.display = 'inline-block'; // Or 'block'
      }
    })
    .catch(error => {
      // Hide loading state and show error
      generateButton.classList.remove('generating');
      generateButton.disabled = false;
      generatedContentDiv.textContent = 'Error generating content. Please try again.';
      console.error('Error generating content:', error);
    });
  }

  // Commenting out the CSRF token fetching logic since CORS is disabled on the backend
    fetch('https://aighostwriter.kurtastarita.com/generate', {
  // .then(response => {
  //   if (!response.ok) {
  //     return response.text().then(text => {
  //       throw new Error(`HTTP error! status: ${response.status}, body: ${text}`);
  //     });
  //   }
  //   return response.json();
  // })
  // .then(data => {
  //   csrfToken = data.csrf_token; // Store the CSRF token from the response
  //   generateButton.addEventListener('click', generateContent);
  // })
  // .catch(error => {
  //   console.error('Error fetching CSRF token:', error);
  // });

  generateButton.addEventListener('click', generateContent); // Ensure the event listener is still attached

  // Add event listener for copy button (if it exists)
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
            copyButton.disabled = false;
            generatedContentDiv.classList.remove('loading');
            alert('Failed to copy content.');
          });
      } else {
        alert('No content to copy.');
      }
    });
  }
});
