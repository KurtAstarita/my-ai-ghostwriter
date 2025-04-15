const generateForm = document.getElementById('generateForm');
const generateButton = generateForm.querySelector('button[type="button"]');
const generatedContent = document.getElementById('generatedContent');

function getCookie(name) {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
}

function generateContent() {
    const backstory = document.getElementById('backstory').value;
    const samples = document.getElementById('samples').value;
    const prompt = document.getElementById('prompt').value;

    const data = {
        backstory: backstory,
        samples: samples,
        prompt: prompt
    };

    generateButton.classList.add('generating');
    generateButton.innerText = 'Generating content...';
    generatedContent.classList.add('loading');
    generatedContent.value = 'Generating... Please wait.';

    fetch('https://my-ai-ghostwriter.onrender.com/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrf_token')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        generateButton.classList.remove('generating');
        generateButton.innerText = 'Generate Badass Content';
        generatedContent.classList.remove('loading');
        generatedContent.value = DOMPurify.sanitize(data.generated_content);
    })
    .catch((error) => {
        console.error('Error:', error);
        generateButton.classList.remove('generating');
        generateButton.innerText = 'Generate Badass Content';
        generatedContent.classList.remove('loading');
        generatedContent.value = 'Error generating content.';
    });
}

// Fetch CSRF token on page load and then attach the event listener
fetch('https://my-ai-ghostwriter.onrender.com/csrf_token')
    .then(response => response.json()) // We don't actually need the JSON response, the cookie will be set
    .then(() => {
        generateButton.addEventListener('click', generateContent);
    })
    .catch(error => {
        console.error('Error fetching CSRF token:', error);
        // Optionally handle the error, e.g., disable the generate button
    });
