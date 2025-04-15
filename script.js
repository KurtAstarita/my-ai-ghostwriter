        const lengthSelect = document.getElementById('length');
        const customLengthInput = document.getElementById('customLength');
        const languageSelect = document.getElementById('language');
        const otherLanguageInput = document.getElementById('otherLanguage');
        const outputDiv = document.getElementById('output');
        const resultText = document.getElementById('result-text');
        const form = document.getElementById('ghostwriter-form');

        lengthSelect.addEventListener('change', function() {
            customLengthInput.style.display = this.value === 'custom' ? 'block' : 'none';
        });

        languageSelect.addEventListener('change', function() {
            otherLanguageInput.style.display = this.value === 'other' ? 'block' : 'none';
        });

        form.addEventListener('submit', function(event) {
            event.preventDefault();
            outputDiv.style.display = 'block';
            resultText.innerText = 'Generating your writing... Please wait.';

            const formData = new FormData(this);
            const data = {};
            formData.forEach((value, key) => {
                data[key] = value;
            });

            // In a real application, you would send 'data' to your backend server
            console.log('Form Data:', data);

            // Simulate a response after a short delay (for demonstration purposes)
            setTimeout(() => {
                const generatedText = `This is a sample generated text based on your prompt: "${data.prompt}". The content type is "${data.contentType}" with a tone of "${data.tone}".`;
                resultText.innerText = generatedText;
            }, 2000);
        });
