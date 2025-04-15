const generateForm = document.getElementById('generateForm');
const generateButton = generateForm.querySelector('button[type="button"]');
const generatedContent = document.getElementById('generatedContent');

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
    generatedContent.value = 'Generating... Please wait.'; // Optional: Add a message in the textarea

    fetch('https://my-ai-ghostwriter.onrender.com/generate', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
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
