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
            
            // Re-attach copy event listeners
            attachCopyListeners();
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Failed to generate excuses. Please try again.');
    } finally {
        button.textContent = originalButtonText;
        button.disabled = false;
    }
});

// Function to show notification
function showNotification(message) {
    const notification = document.getElementById('copyNotification');
    notification.textContent = message;
    notification.classList.add('show');
    
    setTimeout(() => {
        notification.classList.remove('show');
    }, 2000);
}

// Function to copy text to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text)
        .then(() => {
            showNotification('Copied to clipboard!');
        })
        .catch(err => {
            console.error('Failed to copy: ', err);
            showNotification('Failed to copy!');
        });
}

// Function to attach copy event listeners
function attachCopyListeners() {
    // Individual copy buttons
    document.querySelectorAll('.copy-btn').forEach(button => {
        button.addEventListener('click', function() {
            const text = this.getAttribute('data-text');
            copyToClipboard(text);
        });
    });
    
    // Copy all button
    const copyAllBtn = document.querySelector('.copy-all-btn');
    if (copyAllBtn) {
        copyAllBtn.addEventListener('click', function() {
            const excuseTexts = Array.from(document.querySelectorAll('.excuse-text'))
                .map(el => el.textContent.trim())
                .join('\n');
            copyToClipboard(excuseTexts);
        });
    }
}

// Initial attachment of event listeners
document.addEventListener('DOMContentLoaded', function() {
    attachCopyListeners();
});