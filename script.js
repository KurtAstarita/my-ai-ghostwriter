function generateContent() {
    const backstory = document.getElementById('backstory').value;
    const samples = document.getElementById('samples').value;
    const prompt = document.getElementById('prompt').value;

    const data = {
        backstory: backstory,
        samples: samples,
        prompt: prompt
    };

    fetch('https://my-ai-ghostwriter.onrender.com/generate', { // Replace with your actual PythonAnywhere URL
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        document.getElementById('generatedContent').value = data.generated_content;
    })
    .catch((error) => {
        console.error('Error:', error);
        document.getElementById('generatedContent').value = 'Error generating content.';
    });
}
