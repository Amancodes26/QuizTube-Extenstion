document.addEventListener('DOMContentLoaded', function() {
    // Get current tab URL
    chrome.tabs.query({active: true, currentWindow: true}, function(tabs) {
        const currentUrl = tabs[0].url;
        document.getElementById('current-url').textContent = currentUrl;
    });

    document.getElementById('generate-quiz').addEventListener('click', async () => {
        const statusDiv = document.getElementById('status');
        const quizDiv = document.getElementById('quiz-result');
        const button = document.getElementById('generate-quiz');
        
        try {
            button.innerHTML = '<div class="loading"></div>';
            statusDiv.textContent = '🔄 Processing video...';
            quizDiv.textContent = '';  // Clear previous results

            const response = await fetch('http://localhost:5000/generate-quiz', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url: document.getElementById('current-url').textContent
                })
            });

            const data = await response.json();
            
            if (data.success && data.data && data.data.quiz) {
                statusDiv.textContent = '✅ Quiz generated successfully!';
                quizDiv.textContent = data.data.quiz;
            } else {
                throw new Error(data.error || 'Failed to generate quiz');
            }
        } catch (error) {
            console.error('Error:', error);
            statusDiv.textContent = '❌ Error: ' + (error.message || 'Failed to connect to server');
            quizDiv.innerHTML = '<div class="error">Please try again. If the problem persists, check if the backend server is running.</div>';
        } finally {
            button.textContent = 'Generate Quiz';
        }
    });
});
