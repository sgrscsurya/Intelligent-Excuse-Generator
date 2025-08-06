document.getElementById("excuseForm").addEventListener("submit", async function(e) {
    e.preventDefault();
    
    const button = this.querySelector("button");
    const originalButtonText = button.textContent;
    button.textContent = "Generating...";
    button.disabled = true;
    
    try {
        const formData = new FormData(this);
        const response = await fetch("/generate", {
            method: "POST",
            body: formData
        });
        
        if (!response.ok) throw new Error('Network response was not ok');
        
        const html = await response.text();
        const parser = new DOMParser();
        const doc = parser.parseFromString(html, 'text/html');
        const newResults = doc.querySelector('.results-container');
        
        if (newResults) {
            const currentResults = document.querySelector('.results-container');
            if (currentResults) {
                currentResults.replaceWith(newResults);
            } else {
                this.insertAdjacentElement('afterend', newResults);
            }
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate excuses. Please try again.');
    } finally {
        button.textContent = originalButtonText;
        button.disabled = false;
    }
});