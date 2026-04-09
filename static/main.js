/**
 * URL Shortener Client-Side Functionality
 * @module main
 */

/**
 * Copies the shortened URL to the user's clipboard.
 * 
 * Creates a temporary textarea element, selects its content,
 * executes the copy command, and displays a success message.
 * The temporary element is then removed from the DOM.
 * 
 * @function copyToClipboard
 * @returns {void}
 * 
 * @example
 * // HTML element with id="short-link" containing the URL to copy
 * <p id="short-link">https://short.url/abc123</p>
 * <button onclick="copyToClipboard()">Copy</button>
 */
function copyToClipboard() {
    const shortLink = document.getElementById('short-link');
    const textArea = document.createElement('textarea');
    textArea.value = shortLink.textContent;
    document.body.appendChild(textArea);
    textArea.select();
    document.execCommand('copy');
    document.body.removeChild(textArea);
            
    const message = document.getElementById('copy-message');
    message.style.display = 'block';
    setTimeout(() => {
        message.style.display = 'none';
    }, 2000);
}

/**
 * Initializes fade-in animation for the main container on page load.
 * 
 * Sets initial opacity and transform values, then applies transitions
 * after a short delay to create a smooth entrance animation.
 * 
 * @listens DOMContentLoaded
 * @returns {void}
 */
document.addEventListener('DOMContentLoaded', function() {
    const container = document.querySelector('.container');
        if (container) {
            container.style.opacity = '0';
            container.style.transform = 'translateY(20px)';
                
            setTimeout(() => {
                container.style.transition = 'all 0.6s ease';
                container.style.opacity = '1';
            container.style.transform = 'translateY(0)';
        }, 100);
    }
});